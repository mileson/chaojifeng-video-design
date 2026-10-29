"""Exact template-name routing; no renderer, network or product assets."""
import contextlib
import io
import json
import unittest
from unittest.mock import patch
import catalog as cli


class CatalogNameTests(unittest.TestCase):
    def run_cli(self, args, entries=None):
        output = io.StringIO()
        with patch('sys.argv', ['catalog.py', *args, '--json']), contextlib.redirect_stdout(output):
            if entries is None:
                status = cli.main()
            else:
                with patch.object(cli, 'catalog', return_value=entries):
                    status = cli.main()
        return status, json.loads(output.getvalue())

    def test_real_template_id_name_and_alias(self):
        for value in ['product-split-explainer', '极简左右讲解', ' MINIMAL SPLIT EXPLAINER ']:
            status, result = self.run_cli(['--kind', 'recipe', 'get', value])
            self.assertEqual(status, 0)
            self.assertEqual(result['item']['id'], 'product-split-explainer')

    def test_scenario_contains_template(self):
        status, result = self.run_cli(['--kind', 'recipe', 'list', '--scenario', 'product-promo'])
        self.assertEqual(status, 0)
        self.assertIn('product-split-explainer', [x['id'] for x in result['items']])

    def test_product_promo_styles_are_visible_in_gallery(self):
        from build_gallery import gallery_data
        data = gallery_data()
        self.assertIn('product-promo', {x['id'] for x in data['scenarios']})
        visible = {x['id'] for x in data['styles'] if 'product-promo' in x['scenario_ids']}
        self.assertTrue({'product-minimal', 'paper-editorial', 'dual-ground-launch'} <= visible)

    def test_unknown_is_not_a_fuzzy_fallback(self):
        status, result = self.run_cli(['--kind', 'recipe', 'get', '左右'])
        self.assertEqual(status, 2)
        self.assertIn('unknown', result['error'])

    def test_ambiguous_name_requires_id(self):
        entries = {key: {'id': key, 'name': 'Same', 'aliases': []} for key in ['one', 'two']}
        status, result = self.run_cli(['--kind', 'recipe', 'get', 'same'], entries)
        self.assertEqual(status, 2)
        self.assertIn('ambiguous', result['error'])
        status, result = self.run_cli(['--kind', 'recipe', 'get', 'one'], entries)
        self.assertEqual(status, 0)
        self.assertEqual(result['item']['id'], 'one')

    def test_style_alias_still_works(self):
        entries = {'style-one': {'id': 'style-one', 'name': 'Paper', 'aliases': ['纸面']}}
        status, result = self.run_cli(['--kind', 'style', 'get', '纸面'], entries)
        self.assertEqual(status, 0)
        self.assertEqual(result['item']['id'], 'style-one')


if __name__ == '__main__':
    unittest.main()
