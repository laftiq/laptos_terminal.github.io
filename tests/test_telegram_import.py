import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('importer', Path(__file__).parents[1] / 'scripts/telegram-import.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FakeAPI:
    def __init__(self): self.downloads = 0
    def download(self, file_id):
        self.downloads += 1
        return b'\x89PNG\r\n\x1a\n' + b'test-image'

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'albums').mkdir()
        for album in mod.ALBUMS:
            (self.root / 'albums' / (album + '.html')).write_text('<article></article>')
        self.api = FakeAPI()
    def tearDown(self): self.tmp.cleanup()
    def message(self, owner=42, caption='#street A < B & C'):
        return {'from': {'id': owner}, 'chat': {'id': owner, 'type': 'private'}, 'caption': caption,
                'document': {'file_id': 'file', 'file_size': 25}}
    def test_owner_imports_escaped_caption(self):
        offset, replies = mod.process_updates(self.api, [{'update_id': 10, 'message': self.message()}], 42, self.root, 0)
        self.assertEqual(offset, 11)
        self.assertEqual(len(list((self.root / 'assets/photos/street').glob('*.png'))), 1)
        self.assertIn('A &lt; B &amp; C', (self.root / 'albums/street.html').read_text())
        self.assertIn('Added to street', replies[0]['text'])
    def test_other_users_cannot_upload(self):
        mod.process_updates(self.api, [{'update_id': 1, 'message': self.message(owner=99)}], 42, self.root, 0)
        self.assertEqual(self.api.downloads, 0)
    def test_no_owner_fails_closed(self):
        mod.process_updates(self.api, [{'update_id': 1, 'message': self.message()}], None, self.root, 0)
        self.assertEqual(self.api.downloads, 0)
    def test_duplicate_is_not_appended(self):
        mod.import_photo(self.api, self.message(), self.root)
        reply = mod.import_photo(self.api, self.message(), self.root)
        self.assertIn('already', reply)
        self.assertEqual((self.root / 'albums/street.html').read_text().count('<figure>'), 1)
    def test_multiple_or_missing_tags_rejected(self):
        for caption in ['photo', '#street #autumn photo']:
            mod.import_photo(self.api, self.message(caption=caption), self.root)
        self.assertEqual(self.api.downloads, 0)
    def test_large_file_not_downloaded(self):
        message = self.message(); message['document']['file_size'] = mod.LIMIT + 1
        self.assertIn('larger', mod.import_photo(self.api, message, self.root))
        self.assertEqual(self.api.downloads, 0)
    def test_old_updates_are_ignored(self):
        offset, replies = mod.process_updates(self.api, [{'update_id': 1, 'message': self.message()}], 42, self.root, 2)
        self.assertEqual(offset, 2); self.assertEqual(replies, [])
        self.assertEqual(self.api.downloads, 0)
    def test_id_command_available_before_setup(self):
        message = {'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}, 'text': '/id'}
        _, replies = mod.process_updates(self.api, [{'update_id': 1, 'message': message}], None, self.root, 0)
        self.assertIn('42', replies[0]['text'])

if __name__ == '__main__': unittest.main()
