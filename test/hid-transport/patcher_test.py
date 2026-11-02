#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('patcher',ROOT/'build/ci/patch-stock-hid-transport.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
SOURCE=Path(sys.argv.pop(1))
class PatcherTest(unittest.TestCase):
    def test_hash_locked_patch_versions_entire_asset_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'dist';shutil.copytree(SOURCE,dest)
            receipt=p.patch(dest,Path(tmp)/'receipt.json')
            self.assertEqual(receipt['original_console_sha256'],p.EXPECTED)
            old=[Path(r['before']).name for r in receipt['files'] if r['before']!=r['after']]
            text='\n'.join(f.read_text() for f in dest.rglob('*') if f.suffix in ('.js','.html','.css'))
            for name in old:self.assertNotIn(name,text)
            for f in receipt['files']:
                self.assertEqual(p.sha((dest/f['after']).read_bytes()),f['sha256_after'])
    def test_mismatched_hash_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'dist';shutil.copytree(SOURCE,dest)
            asset=next(f for f in dest.rglob('*') if f.is_file() and p.sha(f.read_bytes())==p.EXPECTED)
            asset.write_bytes(asset.read_bytes()+b'changed')
            before={str(f.relative_to(dest)):f.read_bytes() for f in dest.rglob('*') if f.is_file()}
            with self.assertRaises(ValueError):p.patch(dest,Path(tmp)/'receipt.json')
            self.assertEqual(before,{str(f.relative_to(dest)):f.read_bytes() for f in dest.rglob('*') if f.is_file()})
    def test_wrong_occurrence_count_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'dist';shutil.copytree(SOURCE,dest)
            previous=p.REPLACEMENTS;p.REPLACEMENTS=[('nonexistent-qualified-snippet','x')]
            try:
                with self.assertRaises(ValueError):p.patch(dest,Path(tmp)/'receipt.json')
                self.assertTrue(any(f.is_file() and p.sha(f.read_bytes())==p.EXPECTED for f in dest.rglob('*')))
            finally:p.REPLACEMENTS=previous
if __name__=='__main__':unittest.main()
