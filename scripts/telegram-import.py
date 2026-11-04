#!/usr/bin/env python3
"""Import owner-approved Telegram photo documents into static albums."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.telegram-import-state.json'
REPLIES = Path(os.environ.get('RUNNER_TEMP', '/tmp')) / 'laptos-telegram-replies.json'
ALBUMS = ('street', 'autumn', 'teriberka')
LIMIT = 20 * 1024 * 1024
HELP = 'Send an image as a FILE, with #street, #autumn or #teriberka in its caption. Other text becomes the photo caption. You can forward files and add a caption. To find your ID: /id. Publication is checked approximately every 15 minutes.'

class BotError(Exception):
    pass

class API:
    def __init__(self, token):
        self.token = token

    def call(self, method, **payload):
        request = urllib.request.Request(
            'https://api.telegram.org/bot' + self.token + '/' + method,
            data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
        except (OSError, ValueError):
            raise BotError('Telegram request failed: ' + method) from None
        if not result.get('ok'):
            raise BotError('Telegram rejected request: ' + method)
        return result['result']

    def download(self, file_id):
        info = self.call('getFile', file_id=file_id)
        if info.get('file_size', 0) > LIMIT:
            raise BotError('File exceeds 20 MB')
        url = 'https://api.telegram.org/file/bot' + self.token + '/' + info['file_path']
        try:
            with urllib.request.urlopen(url, timeout=90) as response:
                content = response.read(LIMIT + 1)
        except OSError:
            raise BotError('Telegram file download failed') from None
        if len(content) > LIMIT:
            raise BotError('File exceeds 20 MB')
        return content

def image_extension(data):
    if data.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return '.webp'
    return None

def album_caption(caption):
    tags = set(re.findall(r'(?<!\w)#(street|autumn|teriberka)\b', caption, re.I))
    tags = {tag.lower() for tag in tags}
    if len(tags) != 1:
        return None, ''
    album = tags.pop()
    text = re.sub(r'(?<!\w)#' + album + r'\b', '', caption, flags=re.I).strip()
    return album, text

def import_photo(api, message, root):
    document = message.get('document')
    if not document:
        return HELP
    album, caption = album_caption(message.get('caption', ''))
    if not album:
        return 'Add exactly one album tag: #street, #autumn or #teriberka. Then resend the file.'
    if document.get('file_size', 0) > LIMIT:
        return 'This file is larger than 20 MB. Send a smaller JPG, PNG or WebP.'
    data = api.download(document['file_id'])
    extension = image_extension(data)
    if not extension:
        return 'Unsupported file. Send a JPG, PNG or WebP image as a file.'
    digest = hashlib.sha256(data).hexdigest()[:24]
    relative = Path('assets/photos') / album / (digest + extension)
    path = root / relative
    page = root / 'albums' / (album + '.html')
    markup = page.read_text()
    image_url = '../' + relative.as_posix()
    if 'src="' + image_url + '"' in markup:
        return 'This photo is already in ' + album + '.'
    if '</article>' not in markup:
        raise BotError('Album page structure is invalid')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    alt = caption or (album.capitalize() + ' photograph')
    figure = '<figure><img src="' + image_url + '" alt="' + html.escape(alt, quote=True) + '" loading="lazy">'
    if caption:
        figure += '<figcaption>' + html.escape(caption) + '</figcaption>'
    figure += '</figure>'
    page.write_text(markup.replace('</article>', figure + '</article>', 1))
    return 'Added to ' + album + ': https://laptos.fun/albums/' + album + '\nThe site deployment may take a few minutes.'

def process_updates(api, updates, owner_id, root, offset):
    replies = []
    for update in updates:
        if update['update_id'] < offset:
            continue
        message = update.get('message') or {}
        sender = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '').split('@')[0].strip()
        # ID lookup exposes only the sender's own ID; no media is accepted before owner authorization.
        if chat.get('type') == 'private' and text == '/id':
            replies.append({'chat_id': chat['id'], 'text': 'Your Telegram user ID: ' + str(sender.get('id'))})
        elif chat.get('type') == 'private' and sender.get('id') == owner_id:
            reply = HELP if text in ('/start', '/help') else import_photo(api, message, root)
            replies.append({'chat_id': chat['id'], 'text': reply})
        offset = max(offset, update['update_id'] + 1)
    return offset, replies

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notify', action='store_true')
    args = parser.parse_args()
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    if not token:
        print('TELEGRAM_BOT_TOKEN is not configured. Nothing to do.')
        return
    api = API(token)
    if args.notify:
        if REPLIES.exists():
            for reply in json.loads(REPLIES.read_text()):
                api.call('sendMessage', **reply)
        return
    if api.call('getWebhookInfo').get('url'):
        raise BotError('A webhook is configured for this bot. Use a separate bot for this importer.')
    raw_owner = os.environ.get('TELEGRAM_OWNER_ID', '')
    if raw_owner and not raw_owner.isdigit():
        raise BotError('TELEGRAM_OWNER_ID must be a numeric Telegram user ID')
    owner_id = int(raw_owner) if raw_owner else None
    state = json.loads(STATE.read_text()) if STATE.exists() else {'offset': 0}
    updates = api.call('getUpdates', offset=state['offset'], limit=100, timeout=0, allowed_updates=['message'])
    offset, replies = process_updates(api, updates, owner_id, ROOT, state['offset'])
    if offset != state['offset']:
        STATE.write_text(json.dumps({'offset': offset}) + '\n')
    REPLIES.write_text(json.dumps(replies))
    print('Processed updates:', len(updates), '| owner configured:', bool(owner_id))

if __name__ == '__main__':
    try:
        main()
    except BotError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
