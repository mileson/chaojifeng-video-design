#!/usr/bin/env python3
"""Compile plan bindings, audit observed samples, and scope rebuilds. Standard library only.

Never executes project code, renders media, or certifies visual/audio quality.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def project_file(root, name):
    require(isinstance(name, str) and name and not Path(name).is_absolute(), 'use project-relative input paths')
    path = (root / name).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(), 'missing/outside project input: ' + name)
    return path


def dependency_order(bindings):
    by_id = {b['id']: b for b in bindings}
    require(len(by_id) == len(bindings), 'duplicate binding id')
    visiting, done, order = set(), set(), []

    def visit(key):
        require(key in by_id, 'unknown binding dependency: ' + str(key))
        require(key not in visiting, 'binding dependency cycle: ' + key)
        if key in done:
            return
        visiting.add(key)
        for dep in by_id[key].get('uses', []):
            visit(dep)
        visiting.remove(key)
        done.add(key)
        order.append(key)
    for key in by_id:
        visit(key)
    return order


def compile_bundle(plan_path, spec_path):
    plan_path, spec_path = Path(plan_path), Path(spec_path)
    plan, spec, root = read(plan_path), read(spec_path), spec_path.parent.resolve()
    # Existing plans retain their contract; this optional sidecar does not change schema v1.
    from validate_plan import validate_plan
    result = validate_plan(plan, plan_path)
    require(not result['errors'], 'invalid plan: ' + canonical(result['errors']))
    require(type(spec.get('schema_version')) is int and spec['schema_version'] == 1, 'execution schema_version must be 1')
    require(spec.get('plan_sha256') == file_hash(plan_path), 'stale execution plan hash')
    require(type(spec.get('deterministic')) is bool, 'declare deterministic true/false')
    output = plan['output']
    fps, duration = output['fps'], output['duration_seconds']
    count = round(fps * duration)
    require(count > 0, 'empty frame range')
    sources, elements = {}, {}
    for scene in plan['scenes']:
        sources[scene['id']] = (scene, scene['start'], scene['end'], scene)
        for el in scene['elements']:
            elements[el['id']] = (el, scene['id'])
        for key in ('motions', 'beats', 'narration', 'audio_cues'):
            for item in scene.get(key, []):
                start = item.get('start', item.get('time', scene['start']))
                end = item.get('end', start + item.get('duration_seconds', 0))
                sources[item['id']] = (item, start, end, scene)
    hashes = {}
    def input_hash(name):
        if name not in hashes:
            hashes[name] = file_hash(project_file(root, name))
        return hashes[name]
    shared = {name: input_hash(name) for name in spec.get('inputs', [])}
    raw_bindings = spec.get('bindings')
    require(isinstance(raw_bindings, list) and raw_bindings, 'nonempty bindings required')
    dependency_order(raw_bindings)
    covered = {b.get('source_id') for b in raw_bindings}
    required_sources = {m['id'] for s in plan['scenes'] for m in s.get('motions', [])} | set(spec.get('required_source_ids', []))
    require(required_sources <= covered, 'unbound required sources: ' + ', '.join(sorted(required_sources - covered)))
    bindings = []
    for raw in raw_bindings:
        require(isinstance(raw.get('id'), str) and raw['id'], 'binding id required')
        require(raw.get('source_id') in sources, 'unresolved source_id')
        item, start, end, scene = sources[raw['source_id']]
        target = raw.get('target_id')
        require(target in elements and elements[target][1] == scene['id'], 'target must belong to source scene')
        if 'target_id' in item:
            require(target == item['target_id'], 'binding target differs from planned motion target')
        require(raw.get('kind') in ('camera', 'subject', 'caption', 'transition', 'audio'), 'unknown binding kind')
        first = min(count - 1, math.ceil(start * fps - 1e-9))
        stop = min(count, max(first + 1, math.ceil(end * fps - 1e-9)))
        peak = None
        if raw.get('peak_id'):
            require(raw['peak_id'] in sources, 'unresolved peak_id')
            peak_source, peak_time, _, _ = sources[raw['peak_id']]
            require('time' in peak_source and start <= peak_time <= end, 'peak must be a timed event inside binding')
            peak = min(stop - 1, max(first, round(peak_time * fps)))
        channels = raw.get('channels', {})
        require(isinstance(channels, dict), 'channels must be an object')
        for name, track in channels.items():
            require(isinstance(track, dict), 'track must be an object: ' + name)
            a, b = track.get('from'), track.get('to')
            require((number(a) and number(b)) or (isinstance(a, list) and isinstance(b, list)
                    and len(a) == len(b) and len(a) > 0 and all(number(x) for x in a + b)), 'invalid track values')
            require(track.get('easing', 'linear') in ('linear', 'smooth', 'hold'), 'unsupported easing')
        require(isinstance(raw.get('implementation'), str), 'implementation file required')
        inputs = {name: input_hash(name) for name in
                  set(raw.get('inputs', []) + [raw['implementation']])}
        pair = raw.get('caption_pair')
        if pair:
            require(raw['kind'] == 'caption', 'caption_pair requires caption binding')
            for lang in ('zh', 'en'):
                ident = pair.get(lang + '_id')
                require(ident in elements and elements[ident][1] == scene['id'], 'caption pair must resolve in scene')
            require(pair['zh_id'] != pair['en_id'], 'caption pair needs two elements')
            require(number(pair.get('max_gap_px')) and pair['max_gap_px'] >= 0, 'declare caption max_gap_px')
        require(type(raw.get('must_change', False)) is bool, 'must_change must be boolean')
        handles = raw.get('handles_frames', 2)
        require(type(handles) is int and handles >= 0, 'handles_frames must be nonnegative integer')
        probes = sorted(set([first, (first + stop - 1) // 2, stop - 1] + ([peak] if peak is not None else [])))
        binding = dict(raw, scene_id=scene['id'], start_frame=first, end_frame=stop,
                       peak_frame=peak, sample_frames=probes, handles_frames=handles,
                       channels=channels, inputs_sha256=inputs)
        # A scene change conservatively rebuilds that scene, including its other bindings.
        binding['signature'] = fingerprint(dict(binding=binding, scene=scene))
        bindings.append(binding)
    global_plan = {k: v for k, v in plan.items() if k not in ('scenes', 'revision')}
    bundle = dict(schema_version=1, project_id=plan['project_id'], plan_sha256=file_hash(plan_path),
                  spec_sha256=file_hash(spec_path), output=output, frame_count=count,
                  deterministic=spec['deterministic'], global_signature=fingerprint(dict(plan=global_plan, inputs=shared)),
                  bindings=bindings, order=dependency_order(bindings))
    bundle['bundle_sha256'] = fingerprint(bundle)
    return bundle


def verify_bundle(bundle):
    require(bundle.get('schema_version') == 1, 'invalid bundle version')
    require(bundle.get('bundle_sha256') == fingerprint({k: v for k, v in bundle.items() if k != 'bundle_sha256'}),
            'bundle hash mismatch')
    dependency_order(bundle['bindings'])


def audit(bundle, trace):
    verify_bundle(bundle)
    require(trace.get('bundle_sha256') == bundle['bundle_sha256'], 'stale trace bundle hash')
    require(isinstance(trace.get('adapter'), str) and trace['adapter'], 'trace adapter required')
    require(trace.get('observation') == 'rendered-state', 'trace must read back rendered state, not planned state')
    errors, warnings, seen = [], [], {}
    width, height = bundle['output']['width'], bundle['output']['height']
    frames = trace.get('frames', [])
    require(isinstance(frames, list) and frames, 'empty observation trace')
    for sample in frames:
        frame = sample.get('frame')
        require(type(frame) is int and 0 <= frame < bundle['frame_count'], 'trace frame out of range')
        require(isinstance(sample.get('states'), dict) and isinstance(sample.get('texts', {}), dict), 'invalid observed state')
        value = canonical({'states': sample['states'], 'texts': sample.get('texts', {})})
        if frame in seen and seen[frame][0] != value:
            errors.append(f'frame {frame}: repeated seek differs')
        seen[frame] = (value, sample)
    for b in bundle['bindings']:
        values, pairs_seen = set(), 0
        for f in b['sample_frames']:
            sample = seen.get(f, (None, {}))[1]
            state = sample.get('states', {}).get(b['id'])
            if not isinstance(state, dict) or not state:
                errors.append(f"{b['id']} frame {f}: missing observed state")
                continue
            values.add(canonical(state))
        if b.get('must_change') and len(values) < 2:
            errors.append(b['id'] + ': required state change not observed')
        pair = b.get('caption_pair')
        if not pair:
            continue
        # Check all supplied active samples, not only the required sparse probes.
        for f, (_, sample) in seen.items():
            if not b['start_frame'] <= f < b['end_frame']:
                continue
            texts = sample.get('texts', {})
            zh, en = texts.get(pair['zh_id'], {}), texts.get(pair['en_id'], {})
            if not zh.get('visible') and not en.get('visible'):
                continue
            boxes = [x.get('box') for x in (zh, en)]
            if not all(x.get('visible') and isinstance(x.get('text'), str) and x['text'].strip() for x in (zh, en)):
                errors.append(f"{b['id']} frame {f}: bilingual group is incomplete")
                continue
            if not all(isinstance(box, list) and len(box) == 4 and all(number(v) for v in box) for box in boxes):
                errors.append(f"{b['id']} frame {f}: missing text bounds")
                continue
            z, e = boxes
            valid_boxes = all(0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height for box in boxes)
            below = 0 <= e[1] - z[3] <= pair['max_gap_px']
            overlap = min(z[2], e[2]) > max(z[0], e[0])
            if not (valid_boxes and below and overlap):
                errors.append(f"{b['id']} frame {f}: English must remain directly below its Chinese group, inside frame")
            pairs_seen += 1
        if not pairs_seen:
            errors.append(b['id'] + ': no jointly visible bilingual sample')
    if len(frames) == len(seen):
        warnings.append('No repeated frame: seek repeatability not checked.')
    return dict(valid=not errors, status='failed' if errors else 'partial', errors=errors, warnings=warnings,
                observed_frames=sorted(seen), bundle_sha256=bundle['bundle_sha256'],
                limits=['Observed-state samples only; adapter reports are not pixel proof.',
                        'No continuous playback, listening, visual quality or audience test performed.'])


def impact(old, new):
    verify_bundle(old)
    verify_bundle(new)
    require(old['project_id'] == new['project_id'], 'cannot compare different projects')
    a, b = ({x['id']: x for x in doc['bindings']} for doc in (old, new))
    full = (old['global_signature'] != new['global_signature'] or not old['deterministic'] or not new['deterministic'])
    changed = {k for k in a.keys() | b.keys() if k not in a or k not in b or a[k]['signature'] != b[k]['signature']}
    affected = set(a) | set(b) if full else set(changed)
    while True:
        expanded = affected | {k for items in (a, b) for k, v in items.items() if set(v.get('uses', [])) & affected}
        if expanded == affected:
            break
        affected = expanded
    windows = []
    for key in affected:
        for items in (a, b):
            if key in items:
                x = items[key]
                windows.append([max(0, x['start_frame'] - x['handles_frames']),
                                min(new['frame_count'], x['end_frame'] + x['handles_frames'])])
    merged = []
    for start, end in sorted(windows):
        if start >= end:
            continue
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return dict(full_rebuild=full, changed=sorted(changed), affected=sorted(affected),
                frame_ranges=[[0, new['frame_count']]] if full else merged,
                reuse_candidates=sorted(set(b) - affected),
                limits='Ranges are half-open rebuild advice. Reuse requires matching cached artifacts and verified dependency completeness; checks must be renewed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command, fields in [('compile', ['plan', 'execution']), ('audit', ['bundle', 'trace']), ('impact', ['old', 'new'])]:
        p = sub.add_parser(command)
        for field in fields:
            p.add_argument(field)
        p.add_argument('--out')
    args = parser.parse_args()
    try:
        if args.command == 'compile':
            result = compile_bundle(args.plan, args.execution)
        elif args.command == 'audit':
            result = audit(read(args.bundle), read(args.trace))
        else:
            result = impact(read(args.old), read(args.new))
        output = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.out:
            Path(args.out).write_text(output)
        else:
            print(output, end='')
        return 1 if result.get('valid') is False else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps(dict(valid=False, error=str(exc)), ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
