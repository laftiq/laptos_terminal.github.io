# Telegram → laptos.fun

Bot: https://t.me/photoslaftqbot

## Setup (once)

1. In repository Settings → Secrets and variables → Actions → New repository secret, create `TELEGRAM_BOT_TOKEN` using the token from BotFather. Never put it in a file or commit.
2. Send `/id` to the bot. In GitHub → Actions → Telegram photos → Run workflow, run the importer manually. It will reply with your numeric user ID. Without an owner ID, all photo imports are rejected.
3. Save that ID as another repository secret, `TELEGRAM_OWNER_ID`.
4. Send a photo as a file with a caption such as `#street Moscow, November 2026`. Run the workflow manually for the first test, or wait for its schedule.

## Daily use

Send or forward JPG, PNG or WebP documents, up to 20 MB each, to the bot. Every document must have exactly one album tag: `#street`, `#autumn`, or `#teriberka`. Other caption text becomes the caption and image description. Files without an album tag are not imported; resend them with a tag. Albums/groups must have a tag on each individual file. Compressed Telegram photos are deliberately not imported; send as File.

The scheduled job runs around every 15 minutes, subject to GitHub queue delays. A manual run is available in Actions. Keep scheduled Actions enabled: Telegram holds uncollected updates for no longer than 24 hours. On inactive public repositories, GitHub can disable scheduled workflows after 60 days.

The bot accepts uploads only in private chat from the configured owner. It does not require channel admin access or read channel history. Forward existing posts to it and add an album tag before sending. Only send content you intend to publish.

## What is stored

Original image bytes go to `assets/photos/<album>/<content-hash>.<extension>`. Album HTML is appended to, and `.telegram-import-state.json` tracks the last processed update. Repeated content in the same album is skipped. Your bot token, Telegram user ID, and replies are not committed. Confirmation messages are sent only after the Git push succeeds. The normal Vercel integration deploys the commit afterward; the bot does not claim deployment is already complete.

No permanent backend, database, or external Python packages are required. GitHub's workflow token handles pushes. If branch protection prevents writing to main or Vercel rejects an automated commit, check Actions and Vercel logs before retrying.
