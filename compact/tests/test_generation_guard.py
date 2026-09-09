import importlib.util
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'tools'))

class GuardTests(unittest.TestCase):
    def test_manual_edit_blocks_all_writes(self):
        spec = importlib.util.find_spec('generation_guard')
        self.assertIsNotNone(spec, 'Generators lack protection against overwriting manual edits')
        from generation_guard import preflight, record
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            a, b = root/'a.sch', root/'b.sym'
            a.write_text('generated'); b.write_text('original')
            record(root, 'test', [a,b])
            a.write_text('manual change')
            with self.assertRaisesRegex(RuntimeError, 'manual'):
                preflight(root, 'test', [a,b])
            self.assertEqual(a.read_text(), 'manual change')
            self.assertEqual(b.read_text(), 'original')
    def test_existing_unregistered_file_is_not_adopted_silently(self):
        spec = importlib.util.find_spec('generation_guard')
        self.assertIsNotNone(spec, 'Missing generation guard')
        from generation_guard import preflight
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d); a = root/'a.sch'; a.write_text('unknown')
            with self.assertRaises(RuntimeError): preflight(root, 'test', [a])
    def test_unchanged_outputs_allow_regeneration(self):
        spec = importlib.util.find_spec('generation_guard')
        self.assertIsNotNone(spec, 'Missing generation guard')
        from generation_guard import preflight, record
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d); a = root/'a.sch'
            preflight(root, 'test', [a]); a.write_text('generated')
            record(root, 'test', [a]); preflight(root, 'test', [a])

if __name__ == '__main__': unittest.main()
