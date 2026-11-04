# laptos.fun

Personal website: [laptos.fun](https://laptos.fun). Plain HTML, CSS and JavaScript; Vercel serves the files directly.

## Editing the site

- `index.html` — homepage content, links, bio and workspace.
- `assets/css/base.css` — palette, fonts, glow, window panels and title bars.
- `assets/css/home.css` — homepage components and responsive layouts, grouped by section.
- `assets/css/pages.css` — shared album/banner page frame.
- `assets/css/albums.css`, `banner.css` — styles specific to those pages.
- `assets/js/clock.js` — Moscow clock.
- `assets/js/neofetch.js` — PC/Homelab data and tab switching.
- `assets/js/listening.js` — Last.fm account, polling and relative listening time. The client uses a public read API key, never a session token.
- `assets/js/gallery.js` — original-photo viewer, keyboard controls and swipe gestures.
- `assets/js/banner.js` — copy the 88 × 31 banner HTML.
- `albums/*.html` — album photographs and captions.

Change shared colors and glow in `base.css`. Change a section in its existing component rules in `home.css`; keep tablet and phone adjustments in the responsive sections at the end. Avoid adding another override stylesheet or inline styles.

## Local preview

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Open <http://127.0.0.1:8080>. There is no build step. Node is only needed for development tools. Vercel Analytics is provided by Vercel, so its script is absent in the local Python server.

## Checks and formatting

```sh
python3 -m pip install -r scripts/photo-requirements.txt
python3 -m unittest discover -s tests -v
npm ci
npm run format
npx playwright install chromium
npm run test:browser
```

`npm run format:check` checks formatting without changing files. Browser tests cover responsive widths, the clock, Neofetch tabs, Last.fm states, album navigation and banner copying. Last.fm responses are mocked in the tests.

## Adding photographs

See [ADDING-PHOTOS.md](ADDING-PHOTOS.md) for manual uploads and [TELEGRAM-PHOTOS.md](TELEGRAM-PHOTOS.md) for the Telegram bot.

Original photographs stay in `assets/photos/` (plus the original album covers in `assets/`). `scripts/build-photo-previews.py` generates WebP previews and `albums/metadata.json`, and refreshes album counts on the homepage. It keeps existing HTML indentation. Run it after manual photo edits:

```sh
python3 scripts/build-photo-previews.py
```

The Telegram workflow handles import, preview generation and publication automatically. `.telegram-import-state.json` tracks processed updates and must be preserved. Bot credentials belong in GitHub Actions secrets, as described in the Telegram guide.

## Publishing

Changes pushed to `main` deploy through the connected Vercel project. The GitHub Actions checks also run the importer tests and browser tests.
