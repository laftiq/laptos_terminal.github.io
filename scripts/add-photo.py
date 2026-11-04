#!/usr/bin/env python3
"""Append a photo to an existing album without hand-editing HTML."""
import argparse
import html
from pathlib import Path
import re
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('album', choices=['street', 'autumn', 'teriberka'])
parser.add_argument('photo', type=Path)
parser.add_argument('--caption', default='')
parser.add_argument('--alt', required=True, help='Short description of the photograph')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = args.photo.expanduser().resolve()
if not source.is_file() or source.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp', '.avif'}:
    parser.error('Provide an existing JPG, PNG, WebP or AVIF image.')
page = root / 'albums' / (args.album + '.html')
markup = page.read_text()
if '</article>' not in markup:
    parser.error('Album markup is missing its article closing tag.')
folder = root / 'assets' / 'photos' / args.album
folder.mkdir(parents=True, exist_ok=True)
name = re.sub(r'[^a-zA-Z0-9_-]+', '-', source.stem).strip('-') or 'photo'
destination = folder / (name + source.suffix.lower())
index = 2
while destination.exists():
    destination = folder / (name + '-' + str(index) + source.suffix.lower())
    index += 1
shutil.copy2(source, destination)
url = '../' + destination.relative_to(root).as_posix()
figure = '<figure><img src="' + url + '" alt="' + html.escape(args.alt, quote=True) + '" loading="lazy">'
if args.caption:
    figure += '<figcaption>' + html.escape(args.caption) + '</figcaption>'
figure += '</figure>'
page.write_text(markup.replace('</article>', figure + '</article>', 1))
subprocess.run([sys.executable, str(root / 'scripts/build-photo-previews.py')], check=True)
print('Added:', destination.relative_to(root))
print('Updated:', page.relative_to(root))
print('Commit and push photos, previews, albums and index.html to publish them.')
