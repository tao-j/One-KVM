#!/usr/bin/env python3
"""Copy only public static assets from the isolated pinned stock image."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import time
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

ORIGIN = 'http://127.0.0.1:18081/'
DEST = Path('web/dist')
PATTERN = re.compile(r'''["'(`]([^\s"'`()<>]+\.(?:js|css|woff2?|ttf|svg|png|webp|ico|jpg))(?:[?#][^"'`()<>\s]*)?["'`)]''')

def main():
    # Bounded readiness for an emulated ARM64 application; never dump logs,
    # which can contain a generated administrator password.
    for attempt in range(90):
        try:
            with urlopen(ORIGIN, timeout=3) as r:
                if r.status == 200:
                    break
        except Exception:
            if attempt == 89:
                raise RuntimeError('Isolated stock frontend did not become ready') from None
            time.sleep(2)
    DEST.mkdir(parents=True, exist_ok=True)
    pending, files, total = ['index.html'], {}, 0
    while pending:
        name = pending.pop()
        if name in files:
            continue
        if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or len(files) >= 1500:
            raise RuntimeError('Unsafe asset graph')
        with urlopen(urljoin(ORIGIN, '' if name == 'index.html' else name), timeout=15) as r:
            data = r.read(8 * 1024 * 1024 + 1)
            if len(data) > 8 * 1024 * 1024 or (name != 'index.html' and 'text/html' in r.headers.get('Content-Type', '')):
                raise RuntimeError('Invalid static asset')
        total += len(data)
        if total > 32 * 1024 * 1024:
            raise RuntimeError('Asset budget exceeded')
        out = DEST / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        files[name] = hashlib.sha256(data).hexdigest()
        if name.endswith(('.html', '.js', '.css')):
            for value in PATTERN.findall(data.decode()):
                if value.startswith(('http:', 'https:', '//', 'data:')):
                    continue
                # JS download filenames (e.g. qrcode.png) are not imports.
                if not name.endswith('.css') and not value.startswith(('/', './', '../', 'assets/')):
                    continue
                if value.startswith('assets/'):
                    value = '/' + value
                path = urlparse(urljoin('http://assets/' + name, value)).path.lstrip('/')
                if path.startswith('assets/') or path == 'favicon.png':
                    pending.append(path)
    Path('artifacts').mkdir(exist_ok=True)
    Path('artifacts/stock-frontend-files.json').write_text(json.dumps(files, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'files': len(files), 'bytes': total}))

if __name__ == '__main__':
    main()
