import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
previews = load('previews', ROOT / 'scripts/build-photo-previews.py')
importer = load('importer_previews', ROOT / 'scripts/telegram-import.py')

class PreviewTests(unittest.TestCase):
    def test_original_preserved_idempotent_preview_and_dedup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'albums').mkdir()
            (root / 'albums/street.html').write_text('<article></article>')
            (root / 'index.html').write_text('<a href="albums/street.html"><small>Street</small></a>')
            stream = io.BytesIO()
            Image.new('RGB', (1800, 1200), '#888888').save(stream, 'JPEG')
            data = stream.getvalue()
            class API:
                def download(self, file_id): return data
            message = {'document': {'file_id': 'x'}, 'caption': '#street Test photo'}
            importer.import_photo(API(), message, root)
            metadata = previews.build(root)
            self.assertEqual(metadata['street']['count'], 1)
            original = next((root / 'assets/photos/street').glob('*.jpg'))
            self.assertEqual(original.read_bytes(), data)
            with Image.open(next((root / 'assets/previews').glob('*.webp'))) as image:
                self.assertLessEqual(max(image.size), 1000)
                self.assertNotIn('exif', image.info)
            album = (root / 'albums/street.html').read_text()
            self.assertIn('data-full="../assets/photos/street/', album)
            self.assertIn('already', importer.import_photo(API(), message, root))
            self.assertEqual(previews.build(root), metadata)
            self.assertEqual((root / 'albums/street.html').read_text(), album)

if __name__ == '__main__': unittest.main()
