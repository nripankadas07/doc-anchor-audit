from pathlib import Path
import tempfile
import unittest
from doc_anchor_audit import audit, parse, slug


class Anchors(unittest.TestCase):
    def test_heading_parentheses_duplicates_unicode_and_setext(self):
        d = parse('# Maximum Likelihood Estimator (MLE)\n# Maximum Likelihood Estimator (MLE)\nRésumé\n======\n')
        self.assertEqual(d['anchors'], {'maximum-likelihood-estimator-mle','maximum-likelihood-estimator-mle-1','résumé'})

    def test_code_fences_and_inline_code_not_links(self):
        d = parse('~~~md\n# Fake\n[x](bad.md)\n~~~\n`[y](bad.md)`\n# Real\n')
        self.assertEqual(d['anchors'], {'real'})
        self.assertEqual(d['links'], [])

    def test_cross_file_encoded_fragment_and_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'a.md').write_text('[go][target]\n\n[target]: b.md#r%C3%A9sum%C3%A9\n')
            (root/'b.md').write_text('# Résumé\n')
            out = audit(root)
            self.assertEqual(out['findings'], [])
            self.assertEqual(out['checked_local_links'], 1)

    def test_missing_file_fragment_and_reference_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'a.md').write_text('# A\n[x](missing.md)\n[y](#absent)\n[z][no]\n')
            self.assertEqual([r['kind'] for r in audit(root)['findings']], ['missing-file','missing-anchor','undefined-reference'])

    def test_destination_parentheses_and_custom_anchor(self):
        d = parse('<a id="custom"></a>\n[x](file(1).md#custom)\n')
        self.assertIn('custom', d['anchors'])
        self.assertEqual(d['links'][0][1], 'file(1).md#custom')
        self.assertEqual(d['warnings'], [])

    def test_external_and_root_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'a.md').write_text('[external](https://example.test/a#x)\n[escape](../outside.md)\n')
            out = audit(root)
            self.assertEqual(out['external_links_unchecked'], 1)
            self.assertEqual(out['findings'][0]['kind'], 'outside-root')

    def test_unsupported_scope_visible_and_unclosed_link_rejected(self):
        self.assertTrue(parse('- ## Nested heading\n')['warnings'])
        self.assertTrue(parse('<div>\n')['warnings'])
        with self.assertRaises(ValueError):
            parse('[broken](x.md')

    def test_list_links_shortcut_and_emphasis(self):
        d = parse('- [guide](guide.md)\n[shortcut]\n\n[shortcut]: guide.md\n# _Hello_ variable_name\n')
        self.assertEqual(d['warnings'], [])
        self.assertEqual([v[1] for v in d['links']], ['guide.md', 'guide.md'])
        self.assertEqual(d['anchors'], {'hello-variable_name'})

    def test_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            root = Path(directory)
            target = Path(other)/'secret.md'
            target.write_text('# hidden')
            (root/'link.md').symlink_to(target)
            with self.assertRaises(ValueError):
                audit(root)


if __name__ == '__main__':
    unittest.main()
