#!/usr/bin/env python3
"""Build small WebP album previews and refresh static album metadata."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]

def build(root=ROOT):
    manifest_path = root / 'albums/metadata.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    metadata, preview_by_original = {}, {}
    for page in sorted((root / 'albums').glob('*.html')):
        text = page.read_text()
        fingerprints = []
        def convert(match):
            tag = match.group(0)
            original_match = re.search(r'data-full="([^"]+)"', tag) or re.search(r'src="([^"]+)"', tag)
            original = html.unescape(original_match.group(1))
            source = (page.parent / original).resolve()
            if not source.is_relative_to(root.resolve()) or not source.is_file():
                raise ValueError('Photo source missing or outside repository')
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            fingerprints.append(original + ':' + digest)
            destination = root / 'assets/previews' / (digest[:24] + '.webp')
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with Image.open(source) as image:
                    image = ImageOps.exif_transpose(image)
                    image.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
                    image.convert('RGB').save(destination, 'WEBP', quality=80, method=6)
            with Image.open(destination) as image:
                width, height = image.size
            preview = '../' + destination.relative_to(root).as_posix()
            preview_by_original[source] = destination.relative_to(root).as_posix()
            attributes = {
                'src': preview,
                'data-full': original,
                'width': str(width),
                'height': str(height),
                'decoding': 'async',
            }
            # Update values in place, keeping the page's indentation and attributes.
            for name, value in attributes.items():
                attribute = name + '="' + html.escape(value, quote=True) + '"'
                pattern = r'(?<![\w-])' + name + r'="[^"]*"'
                if re.search(pattern, tag):
                    tag = re.sub(pattern, lambda _: attribute, tag, count=1)
                else:
                    tag = tag.replace('<img', '<img ' + attribute, 1)
            return tag

        # Album pages contain only photo images; favicons are links.
        text = re.sub(r'<img\b[^>]*>', convert, text)
        fingerprint = hashlib.sha256('\n'.join(fingerprints).encode()).hexdigest()
        prior = previous.get(page.stem, {})
        updated = prior.get('updated') if prior.get('fingerprint') == fingerprint else datetime.now(timezone.utc).date().isoformat()
        metadata[page.stem] = {'count': len(fingerprints), 'updated': updated, 'fingerprint': fingerprint}
        page.write_text(text)
    index = root / 'index.html'
    text = index.read_text()
    for album, meta in metadata.items():
        pattern = r'(<a\b[^>]*href="albums/' + re.escape(album) + r'\.html"[^>]*>)(.*?)(</a>)'
        def card(match):
            content = match.group(2)
            image = re.search(r'<img\b[^>]*src="([^"]+)"[^>]*>', content)
            if image:
                source = (root / html.unescape(image.group(1))).resolve()
                # Preserve a previous preview on subsequent runs.
                if source in preview_by_original:
                    content = content.replace('src="' + image.group(1) + '"', 'src="' + preview_by_original[source] + '"', 1)
            count = meta['count']
            label = str(count) + (' photo' if count == 1 else ' photos') + ' · Updated ' + meta['updated']
            meta_pattern = r'(<span class="album-meta"\s*>\s*).*?(\s*</span\s*>)'
            if re.search(meta_pattern, content, flags=re.S):
                content = re.sub(meta_pattern, lambda item: item[1] + label + item[2], content, flags=re.S)
            else:
                content = content.rstrip() + '<span class="album-meta">' + label + '</span>'

            return match.group(1) + content + match.group(3)
        text = re.sub(pattern, card, text, flags=re.S)
    index.write_text(text)
    manifest_path.write_text(json.dumps(metadata, indent=2) + '\n')
    print('Previews ready:', ', '.join(key + '=' + str(value['count']) for key, value in metadata.items()))
    return metadata

if __name__ == '__main__':
    build()
