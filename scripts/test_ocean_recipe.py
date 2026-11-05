"""Regression tests for costly or ambiguous ocean render requests."""
import hashlib
import json
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'objects/water-liquid/runtime'
spec = importlib.util.spec_from_file_location('ocean_config', RUNTIME / 'config.py')
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)

class OceanRecipeTests(unittest.TestCase):
    def setUp(self):
        self.c = cfg.load(RUNTIME / 'presets/open-ocean.json')

    def reject(self, section, key, value):
        self.c[section][key] = value
        with self.assertRaises(cfg.ConfigError):
            cfg.validate(self.c)

    def test_nonfinite_value(self):
        self.reject('ocean', 'wave_scale', float('nan'))

    def test_boolean_is_not_numeric(self):
        self.reject('render', 'threads', True)

    def test_unknown_parameter_rejected(self):
        self.reject('ocean', 'wave_scales', 2)

    def test_thread_budget(self):
        self.reject('render', 'threads', 32)

    def test_undersampled_geometry(self):
        self.reject('grid', 'points', 33)

    def test_bounce_coupling(self):
        self.c['render']['max_bounces'] = 2
        self.reject('render', 'transmission_bounces', 4)

    def test_camera_target_collision(self):
        self.reject('camera', 'target_start', self.c['camera']['start'][:])

    def test_sparse_clip_rejected(self):
        with self.assertRaises(cfg.ConfigError):
            cfg.frames_for(self.c, 'clip', '1,12,24')
        self.assertEqual(cfg.frames_for(self.c, 'frame', '1,12,24'), [1,12,24])

    def test_clip_budget(self):
        count = self.c['render']['max_clip_frames'] + 1
        with self.assertRaises(cfg.ConfigError):
            cfg.frames_for(self.c, 'clip', ','.join(map(str, range(1,count+1))))

    def test_out_of_range_or_duplicate_frames(self):
        for value in ('0','-1','9999','1,1','1.5'):
            with self.subTest(value=value), self.assertRaises(cfg.ConfigError):
                cfg.frames_for(self.c, 'frame', value)

    def test_baseline_matches_implementation_and_preset(self):
        baseline = ROOT / 'objects/water-liquid/baseline'
        evidence = json.loads((baseline / 'verification.json').read_text())
        for name, digest in evidence['source_files'].items():
            self.assertEqual(hashlib.sha256((RUNTIME / name).read_bytes()).hexdigest(), digest,
                             'Implementation changed: rebuild and review baseline')
        self.assertEqual(hashlib.sha256(json.dumps(self.c, sort_keys=True).encode()).hexdigest(),
                         evidence['configuration_sha256'])
        self.assertEqual(json.loads((baseline / 'preset.json').read_text()), self.c)
        for name, digest in evidence['assets'].items():
            self.assertEqual(hashlib.sha256((baseline / name).read_bytes()).hexdigest(), digest)

    def test_default_clip_one_second(self):
        frames = cfg.frames_for(self.c, 'clip')
        self.assertEqual(frames, list(range(1,25)))

if __name__ == '__main__':
    unittest.main()
