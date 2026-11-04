# Adding photographs

Install photo tools once (`python3 -m pip install -r scripts/photo-requirements.txt`). From the repository folder, append a photo to an existing album:

```bash
python3 scripts/add-photo.py street ~/Pictures/my-photo.jpg --alt "Evening street in Moscow" --caption "Moscow, November 2026"
```

Albums: `street`, `autumn`, `teriberka`. The script copies the photo into `assets/photos/<album>/` and adds its HTML entry to the end of the album. Existing files are never overwritten. `--alt` is required; `--caption` is optional. Photos appear in the order added.

Previews and album counts/dates are rebuilt automatically. Publish the generated photos, previews, album pages, metadata and index.html through GitHub; Vercel deploys the commit automatically. The script itself does not push or publish.

Use JPG or WebP around 1600–2400 pixels on the long side for faster loading.

To change an album cover, change its `img.album-cover` source in `index.html`. All album colors live in `albums/album.css`.
