#!/usr/bin/env python3
"""collect_history.py - gather revision evidence for one deliverable family.

Usage:
  python collect_history.py <folder> <base_name> [options]

Options:
  --transcripts DIR [DIR ...]  scan Claude Code transcripts (*.jsonl) under each DIR
  --window                     with --transcripts: list ALL user messages between the first version
                               (-30 min) and the last version (users rarely type file names).
                               Otherwise only messages that mention <base_name>.
  --max-msgs N                 max user messages to print (default 40)
  --full-msgs N                print the first N user messages in full instead of 300 chars
  --handbacks                  with --transcripts: also print subagent/reviewer hand-back reports
                               in the window (first 2500 chars each)
  --diff                       compare consecutive .pptx/.docx/.xlsx versions: pages/slides,
                               pictures, how many pages changed, how many were added
                               (needs python-pptx / python-docx / openpyxl; skipped if missing)

Always: lists every file whose name starts with <base_name> (sorted by version number, with mtime,
size, gap to previous version). NOTE: transcript timestamps are UTC, file mtimes are local time;
the window logic converts. Scope --transcripts to ONE project's folder. Read-only. Prints UTF-8.
"""
import sys, re, json, pathlib, datetime, argparse, hashlib

UTC = datetime.timezone.utc


def ver(name):
    m = re.findall(r'[_ ]v(\d+)', name, re.I)
    return int(m[-1]) if m else 0


def listing(folder, base):
    files = [p for p in pathlib.Path(folder).rglob('*')
             if p.is_file() and p.name.lower().startswith(base.lower()) and not p.name.startswith('~$')]
    files.sort(key=lambda p: (ver(p.name), p.stat().st_mtime))
    prev = None
    print(f'## Versions of "{base}" in {folder}: {len(files)} files')
    for p in files:
        t = datetime.datetime.fromtimestamp(p.stat().st_mtime)
        gap = '' if prev is None else f'  (+{(t - prev).total_seconds() / 60:.0f} min)'
        print(f'{t:%Y-%m-%d %H:%M}  {p.stat().st_size:>10,}  {p.name}{gap}')
        prev = t
    return files


def _h(s):
    s = ' '.join(s.split())  # ignore whitespace-only differences (line breaks, run splits)
    return hashlib.md5(s.encode('utf-8', 'ignore')).hexdigest()[:8]


def pages_of(path):
    """Return (list of per-page text hashes, picture count) or None if unsupported/unavailable."""
    ext = path.suffix.lower()
    try:
        if ext == '.pptx':
            import pptx
            pr = pptx.Presentation(str(path))
            hs, pics = [], 0
            for s in pr.slides:
                txt = ' '.join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
                pics += sum(1 for sh in s.shapes if sh.shape_type == 13)
                hs.append(_h(txt))
            return hs, pics
        if ext == '.xlsx':
            import openpyxl
            wb = openpyxl.load_workbook(str(path), data_only=True, read_only=True)
            hs = []
            for ws in wb.worksheets:
                hs.append(_h(repr([[c for c in row] for row in ws.iter_rows(values_only=True)])))
            return hs, 0
        if ext == '.docx':
            import docx
            d = docx.Document(str(path))
            paras = [p.text for p in d.paragraphs]
            chunk = 20  # compare in blocks of 20 paragraphs
            hs = [_h('\n'.join(paras[i:i + chunk])) for i in range(0, len(paras), chunk)]
            return hs, len(d.inline_shapes)
    except ImportError as e:
        print(f'  (diff skipped for {ext}: {e})')
    except Exception as e:  # locked / corrupt file
        print(f'  (cannot read {path.name}: {e})')
    return None


def diff(files):
    print('\n## Structure diff between consecutive versions (page = slide / sheet / 20-paragraph block)')
    prev = None
    for p in files:
        r = pages_of(p)
        if r is None:
            continue
        hs, pics = r
        if prev is None:
            note = ''
        else:
            ch = sum(1 for a, b in zip(hs, prev) if a != b)
            note = f'  changed={ch} added={max(0, len(hs) - len(prev))} removed={max(0, len(prev) - len(hs))}'
        print(f'{p.name}: pages={len(hs)} pics={pics}{note}')
        prev = hs
    print('Reading: changed=0 with a new version = formatting/layout only; many changed = rewrite or global edit.')


def text_of(msg):
    c = msg.get('content')
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return ' '.join(x.get('text', '') for x in c if isinstance(x, dict) and x.get('type') == 'text')
    return ''


def scan(dirs, base, limit, window, full, handbacks):
    key = base.lower()
    hits, hb = [], []
    for d in dirs:
        for f in pathlib.Path(d).expanduser().rglob('*.jsonl'):
            try:
                with open(f, encoding='utf-8') as fh:
                    for line in fh:
                        if window is None and key not in line.lower():
                            continue
                        try:
                            o = json.loads(line)
                        except ValueError:
                            continue
                        if o.get('type') != 'user':
                            continue
                        t = text_of(o.get('message', {}))
                        ts = o.get('timestamp', '')
                        if window is not None and not (window[0] <= ts <= window[1]):
                            continue
                        if not t:
                            continue
                        if 'Subagent hand-back' in t[:600]:
                            hb.append((ts, t))
                        elif not t.startswith('<') and not t.startswith('[Image'):
                            hits.append((ts, f.parent.name[-30:], t.replace('\n', ' ')))
            except OSError:
                pass
    hits.sort()
    what = 'in the version time window' if window else f'mentioning "{base}"'
    print(f'\n## User messages {what} (UTC timestamps): {len(hits)} (showing {min(len(hits), limit)})')
    for i, (ts, sess, t) in enumerate(hits[:limit]):
        print(f'{ts[:16]}  [{sess}]  {t if i < full else t[:300]}')
    if handbacks:
        hb.sort()
        print(f'\n## Subagent / reviewer hand-back reports in the window: {len(hb)}')
        for ts, t in hb:
            body = t.split('\n', 3)[-1] if t.count('\n') >= 3 else t
            print(f'--- {ts[:16]}\n{body[:2500]}\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('folder'); ap.add_argument('base')
    ap.add_argument('--transcripts', nargs='*', default=[])
    ap.add_argument('--max-msgs', type=int, default=40)
    ap.add_argument('--full-msgs', type=int, default=0)
    ap.add_argument('--window', action='store_true')
    ap.add_argument('--handbacks', action='store_true')
    ap.add_argument('--diff', action='store_true')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    files = listing(a.folder, a.base)
    if a.diff:
        diff(files)
    if a.transcripts:
        win = None
        if a.window and files:
            utc = lambda t: datetime.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%dT%H:%M:%S')
            m = [p.stat().st_mtime for p in files]
            win = (utc(min(m) - 1800), utc(max(m) + 60))
        scan(a.transcripts, a.base, a.max_msgs, win, a.full_msgs, a.handbacks)
