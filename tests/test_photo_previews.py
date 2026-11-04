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

    def test_formatted_html_stays_stable_and_metadata_is_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'albums').mkdir()
            (root / 'assets').mkdir()
            Image.new('RGB', (40, 30)).save(root / 'assets/test.jpg')
            page = root / 'albums/street.html'
            page.write_text('<article class="panel album">\n  <figure>\n    <img\n      src="../assets/test.jpg"\n      alt="Keep this caption"\n    >\n  </figure>\n</article>\n')
            index = root / 'index.html'
            index.write_text('<a\n  href="albums/street.html"\n>\n  <span class="album-meta">\n    99 photos · Updated old\n  </span>\n</a>\n')
            previews.build(root)
            first = (page.read_text(), index.read_text())
            self.assertIn('\n      src="../assets/previews/', first[0])
            self.assertIn('alt="Keep this caption"', first[0])
            self.assertEqual(first[1].count('class="album-meta"'), 1)
            self.assertIn('1 photo · Updated', first[1])
            self.assertNotIn('99 photos', first[1])
            previews.build(root)
            self.assertEqual((page.read_text(), index.read_text()), first)

if __name__ == '__main__': unittest.main()
