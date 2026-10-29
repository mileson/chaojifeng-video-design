import copy
import json
from pathlib import Path
import tempfile
import unittest

from execution_contract import compile_bundle, audit, impact, file_hash

ROOT = Path(__file__).resolve().parents[1]


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = json.loads((ROOT / 'templates/plan.json').read_text())
        self.plan['output'].update(width=1080, height=1920)
        scene = self.plan['scenes'][0]
        scene['elements'] += [dict(id='caption-zh', role='text', content='雨停之后'),
                              dict(id='caption-en', role='text', content='After the rain')]
        self.spec = json.loads((ROOT / 'templates/execution.json').read_text())
        (self.root / 'src').mkdir()
        (self.root / 'src/scene.mjs').write_text('// project implementation\n')
        (self.root / 'src/captions.mjs').write_text('// captions\n')
        self.spec['bindings'].append(dict(id='caption-group', source_id='scene-01', target_id='caption-zh',
            kind='caption', implementation='src/captions.mjs', uses=['reveal-subject'],
            caption_pair=dict(zh_id='caption-zh', en_id='caption-en', max_gap_px=30)))

    def compile(self):
        plan_path = self.root / 'plan.json'
        plan_path.write_text(json.dumps(self.plan))
        self.spec['plan_sha256'] = file_hash(plan_path)
        (self.root / 'execution.json').write_text(json.dumps(self.spec))
        return compile_bundle(plan_path, self.root / 'execution.json')

    def trace(self, bundle):
        frames = sorted({f for b in bundle['bindings'] for f in b['sample_frames']})
        return dict(bundle_sha256=bundle['bundle_sha256'], adapter='test-observer', observation='rendered-state',
            frames=[dict(frame=f, states={b['id']:dict(x=f) for b in bundle['bindings']}, texts={
                'caption-zh':dict(text='雨停之后', visible=True, box=[100,100,400,160]),
                'caption-en':dict(text='After the rain', visible=True, box=[100,172,400,200])}) for f in frames])

    def test_compile_derives_frames_and_noop_impact(self):
        b = self.compile()
        self.assertEqual((b['bindings'][0]['start_frame'], b['bindings'][0]['end_frame']), (30,60))
        self.assertEqual(impact(b,b)['frame_ranges'], [])
        self.assertTrue(audit(b,self.trace(b))['valid'])
        self.assertEqual(audit(b,self.trace(b))['status'], 'partial')

    def test_stale_plan_and_modified_bundle_rejected(self):
        b = self.compile()
        with (self.root/'plan.json').open('a') as f: f.write(' ')
        with self.assertRaisesRegex(ValueError,'stale'):
            compile_bundle(self.root/'plan.json', self.root/'execution.json')
        b['bindings'][0]['start_frame'] = 0
        with self.assertRaisesRegex(ValueError,'hash'):
            audit(b,self.trace(b))

    def test_target_mismatch_and_unbound_motion(self):
        self.spec['bindings'][0]['target_id'] = 'caption-zh'
        with self.assertRaisesRegex(ValueError,'target differs'): self.compile()
        self.spec['bindings'].pop(0)
        self.spec['bindings'][0]['uses'] = []
        with self.assertRaisesRegex(ValueError,'unbound'): self.compile()

    def test_missing_observation_and_frozen_motion(self):
        b = self.compile(); t = self.trace(b)
        for f in t['frames']: f['states']['reveal-subject'] = {'x':0}
        self.assertFalse(audit(b,t)['valid'])
        t = self.trace(b); t['frames'].pop()
        self.assertFalse(audit(b,t)['valid'])

    def test_bilingual_detachment_missing_and_clipping(self):
        b = self.compile()
        for box in ([100,1000,400,1030], [100,90,400,99], [1100,172,1400,200]):
            t = self.trace(b); t['frames'][0]['texts']['caption-en']['box'] = box
            self.assertFalse(audit(b,t)['valid'])
        t = self.trace(b); del t['frames'][0]['texts']['caption-en']
        self.assertFalse(audit(b,t)['valid'])

    def test_seek_difference(self):
        b = self.compile(); t = self.trace(b)
        extra = copy.deepcopy(t['frames'][0]); extra['states']['reveal-subject']['x'] += 1
        t['frames'].append(extra)
        self.assertFalse(audit(b,t)['valid'])

    def test_dependency_closure_and_caption_only_change(self):
        old = self.compile()
        (self.root/'src/scene.mjs').write_text('// revised subject\n')
        new = self.compile()
        self.assertEqual(impact(old,new)['affected'], ['caption-group','reveal-subject'])
        old = new
        (self.root/'src/captions.mjs').write_text('// revised captions\n')
        new = self.compile()
        self.assertEqual(impact(old,new)['reuse_candidates'], ['reveal-subject'])
        self.assertFalse(impact(old,new)['full_rebuild'])

    def test_global_changes_and_stateful_force_full(self):
        old = self.compile(); self.plan['output']['width']=1920
        self.assertTrue(impact(old,self.compile())['full_rebuild'])
        self.plan['output']['width']=1080; self.spec['deterministic']=False
        self.assertTrue(impact(old,self.compile())['full_rebuild'])

    def test_cycle_and_outside_project(self):
        self.spec['bindings'][0]['uses']=['caption-group']
        with self.assertRaisesRegex(ValueError,'cycle'): self.compile()
        self.spec['bindings'][0]['uses']=[]
        self.spec['bindings'][0]['implementation']='../outside.mjs'
        with self.assertRaisesRegex(ValueError,'outside'): self.compile()


if __name__ == '__main__':
    unittest.main()
