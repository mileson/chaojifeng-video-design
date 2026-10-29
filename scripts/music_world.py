#!/usr/bin/env python3
"""Prepare, analyse and validate a music-led 3D project. No network or installs.

Analysis is deliberately labelled candidate: RMS attacks are not verified musical
beats or phrases. The agent refines the generated score after listening.
"""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {'水墨': 'ink', '水墨山河': 'ink', '中国水墨': 'ink', '烟雨': 'rain', '青花': 'rain',
           '理论概念': 'concept', '空间几何': 'concept', '几何': 'concept'}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    def reject(x): raise ValueError('nonfinite JSON: ' + x)
    return json.loads(Path(path).read_text(), parse_constant=reject)


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors='replace')[-1600:])
    return result.stdout


def probe(path):
    data = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path]))
    if not any(s['codec_type'] == 'audio' for s in data['streams']):
        raise ValueError('music has no audio stream')
    return float(data['format']['duration'])


def init(args):
    dest = Path(args.into).expanduser().resolve()
    music = Path(args.music).expanduser().resolve()
    style = ALIASES.get(args.style, args.style)
    if style not in ('ink', 'rain', 'concept'):
        raise ValueError('style must resolve to ink / rain / concept; use a project look for variations')
    if dest.exists(): raise ValueError('destination already exists; reuse it without reinitialising')
    if not music.is_file(): raise ValueError('supply a local audio file; resolve/download URLs before init')
    length = probe(music)
    duration = min(args.duration, length - args.source_in)
    if args.source_in < 0 or duration <= 0: raise ValueError('invalid source window')
    engine = args.engine if args.engine != 'auto' else ('three' if style == 'concept' else 'blender')
    shutil.copytree(ROOT / 'assets/music-world/starter', dest)
    (dest / 'public').mkdir(exist_ok=True)
    write(dest / 'project.json', dict(schema_version=1, theme=args.theme, style=style, engine=engine,
          source=dict(path=str(music), sha256=digest(music), source_in=args.source_in),
          duration=duration, fps=args.fps, width=args.width, height=args.height, seed=2026,
          theme_adaptation='pending', listening='not_run', note='Refine subject, relationships and score for this film.'))
    return dict(project=str(dest), engine=engine, next='analyse, refine scene and score, validate, render')


def percentile(values, fraction):
    return sorted(values)[min(len(values) - 1, int((len(values) - 1) * fraction))]


def normalize(values):
    lo, hi = percentile(values, .05), percentile(values, .99)
    prev, out = 0., []
    for value in values:
        v = min(1., max(0., (value - lo) / max(1e-9, hi - lo)))
        prev = v if v > prev else prev + .25 * (v - prev)
        out.append(round(prev, 4))
    return out


def features(samples, sr, fps, frames):
    # Two first-order lowpasses provide coarse bands, not calibrated spectra.
    a = 1 - math.exp(-2 * math.pi * 150 / sr)
    b = 1 - math.exp(-2 * math.pi * 1800 / sr)
    bands = {k: [] for k in ('low', 'mid', 'high', 'rms')}
    low = midlow = 0.
    for frame in range(frames):
        sums = [0., 0., 0., 0.]
        segment = samples[round(frame * sr / fps):round((frame + 1) * sr / fps)]
        for raw in segment:
            x = raw / 32768
            low += a * (x - low)
            midlow += b * (x - midlow)
            for i, value in enumerate((low, midlow - low, x - midlow, x)):
                sums[i] += value * value
        for key, value in zip(bands, sums):
            bands[key].append(math.sqrt(value / max(1, len(segment))))
    return bands


def attacks(rms, fps):
    novelty = [max(0., x - (sum(rms[max(0, i-4):i]) / max(1, min(4, i)))) for i, x in enumerate(rms)]
    threshold = max(1e-6, percentile(novelty, .72))
    selected = []
    for i in range(1, len(novelty)-1):
        if novelty[i] <= threshold or novelty[i] < novelty[i-1] or novelty[i] < novelty[i+1]: continue
        if selected and i - selected[-1] < fps * .18:
            if novelty[i] > novelty[selected[-1]]: selected[-1] = i
        else: selected.append(i)
    peak = max(novelty, default=1) or 1
    return [dict(id=f'attack-{j+1:03}', time=round(i/fps, 6), strength=round(novelty[i]/peak, 4),
                 status='candidate', kind='attack') for j, i in enumerate(selected)]


def analyse(args):
    project = Path(args.project).resolve()
    cfg = read(project/'project.json')
    source = Path(cfg['source']['path'])
    if digest(source) != cfg['source']['sha256']: raise ValueError('source changed; explicitly choose/reinitialise the source')
    frames = round(cfg['duration'] * cfg['fps'])
    cfg['duration'] = frames / cfg['fps']
    cfg['source']['source_out'] = cfg['source']['source_in'] + cfg['duration']
    run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-threads', '1', '-ss', cfg['source']['source_in'],
         '-i', source, '-t', cfg['duration'], '-vn', '-ac', '2', '-ar', '48000', '-c:a', 'pcm_s16le', project/'public/music.wav'])
    raw = run(['ffmpeg', '-v', 'error', '-nostdin', '-threads', '1', '-i', project/'public/music.wav',
               '-ac', '1', '-ar', '8000', '-f', 's16le', '-'])
    samples = array('h'); samples.frombytes(raw)
    if sys.byteorder != 'little': samples.byteswap()
    bands = features(samples, 8000, cfg['fps'], frames)
    candidates = attacks(bands['rms'], cfg['fps'])
    intervals = [b['time']-a['time'] for a,b in zip(candidates, candidates[1:]) if .3 <= b['time']-a['time'] <= 1.2]
    bpm = round(60/percentile(intervals, .5), 2) if intervals else None
    identity = dict(source_sha256=cfg['source']['sha256'], source_in=cfg['source']['source_in'],
                    duration=cfg['duration'], fps=cfg['fps'])
    analysis = dict(schema_version=1, **identity, method='8000Hz coarse band RMS and attack novelty; no beat/downbeat/phrase verification',
                    candidate_bpm=bpm, bpm_status='candidate' if bpm else 'unknown', anchors=candidates,
                    features={k: normalize(v) for k,v in bands.items()}, audio_sha256=digest(project/'public/music.wav'))
    write(project/'music-analysis.json', analysis)
    cfg['listening'] = 'not_run'
    write(project/'project.json', cfg)
    # Reanalysis never silently overwrites an agent-authored event score.
    scorepath = project/'score.json'
    preserved = scorepath.exists()
    score = dict(schema_version=1, **identity, status='candidate', events=[])
    points = candidates or [dict(time=t, strength=.5) for t in range(1, math.ceil(cfg['duration']), 2)]
    for j, p in enumerate(points):
        t = p['time']
        score['events'].append(dict(id=f'event-{j+1:03}', object_id=f'subject-{j%7}',
            kind={'ink':'ink-impact','rain':'brush-reveal','concept':'relation-settle'}[cfg['style']],
            prepare=max(0, t-.3), trigger=t, peak=t, settle=min(cfg['duration'], t+.15),
            hold_until=min(cfg['duration'], t+.45), strength=p['strength'], anchor_status='candidate',
            meaning='Replace with the actual subject action and relationship.'))
    write(project/'score.candidate.json', score)
    if not scorepath.exists(): write(scorepath, score)
    return dict(frames=frames, attacks=len(candidates), candidate_bpm=bpm, analysis_status='candidate',
                score_preserved=preserved, next='Listen and refine score.json; implement theme; validate before render')


def validate(args):
    project=Path(args.project).resolve(); cfg=read(project/'project.json')
    data=read(project/'music-analysis.json'); score=read(project/'score.json'); errors=[]
    expected=dict(source_sha256=cfg['source']['sha256'],source_in=cfg['source']['source_in'],duration=cfg['duration'],fps=cfg['fps'])
    for name,obj in [('analysis',data),('score',score)]:
        for key,val in expected.items():
            if obj.get(key)!=val: errors.append(f'{name}: stale {key}; reanalyse/remap after changing music or timing')
    if not Path(cfg['source']['path']).is_file() or digest(cfg['source']['path'])!=expected['source_sha256']:
        errors.append('missing or changed source music')
    if not (project/'public/music.wav').exists() or digest(project/'public/music.wav')!=data['audio_sha256']:
        errors.append('missing or changed derived audio')
    n=round(cfg['duration']*cfg['fps'])
    for key,values in data['features'].items():
        if len(values)!=n or any(not math.isfinite(v) or not 0<=v<=1 for v in values):errors.append('invalid feature array '+key)
    ids=set()
    for e in score['events']:
        if e['id'] in ids:errors.append('duplicate event '+e['id'])
        ids.add(e['id'])
        times=[e[k] for k in ('prepare','trigger','peak','settle','hold_until')]
        if any(type(t) not in (int,float) or not math.isfinite(t) for t in times) or times!=sorted(times) or times[0]<0 or times[-1]>cfg['duration']:
            errors.append('invalid event phase '+e['id'])
    if not score['events']: errors.append('score has no events')
    for e in score['events']:
        if not isinstance(e.get('object_id'),str) or not e.get('id'):errors.append('event identity missing')
        if type(e.get('strength')) not in (int,float) or not 0<=e['strength']<=1:errors.append('invalid event strength')
    result=dict(valid=not errors,errors=errors,semantic=cfg.get('theme_adaptation','pending'),listening=cfg.get('listening','not_run'),
                note='Structural checks only; candidate attacks do not prove musical sync or audience understanding.')
    if not errors:
        write(project/'public/job.json',dict(config=cfg,analysis=data,score=score))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('init');s.add_argument('--music',required=True);s.add_argument('--theme',required=True)
    s.add_argument('--style',required=True);s.add_argument('--into',required=True)
    s.add_argument('--duration',type=float,default=60);s.add_argument('--source-in',type=float,default=0)
    s.add_argument('--fps',type=int,default=30);s.add_argument('--width',type=int,default=1080);s.add_argument('--height',type=int,default=1920)
    s.add_argument('--engine',choices=['auto','three','blender'],default='auto')
    for cmd in ('analyse','validate'):
        s=sub.add_parser(cmd);s.add_argument('--project',required=True)
    args=p.parse_args()
    try:
        if args.command=='init' and (args.duration<=0 or args.fps<=0 or args.width<=0 or args.height<=0): raise ValueError('output dimensions, duration and fps must be positive')
        result={'init':init,'analyse':analyse,'validate':validate}[args.command](args)
        print(json.dumps(result,ensure_ascii=False,allow_nan=False))
        return 0 if result.get('valid',True) else 1
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as e:
        print(json.dumps(dict(valid=False,error=str(e)),ensure_ascii=False));return 1


if __name__=='__main__':sys.exit(main())
