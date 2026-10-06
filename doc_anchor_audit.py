"""Check repository-local Markdown targets and heading fragments offline."""
from __future__ import annotations

import argparse
from html import unescape
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

MAX_FILE = 2_000_000
MAX_TOTAL = 20_000_000
MAX_FILES = 1000
IGNORED = {'.git', 'node_modules', '.venv', 'venv', 'dist', 'build'}


def slug(text):
    text = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = unescape(text).strip().lower()
    text = re.sub(r'(?<!\w)_{1,2}(.+?)_{1,2}(?!\w)', r'\1', text)
    text = text.replace('`', '').replace('*', '').replace('~', '')
    text = re.sub(r'[^\w\- ]', '', text, flags=re.UNICODE)
    return text.replace(' ', '-')


def inline_links(line):
    # Suppress code spans while retaining character offsets.
    masked = re.sub(r'(`+).*?\1', lambda m: ' '*len(m[0]), line)
    links = []
    consumed = 0
    pattern = re.compile(r'(?<!!)\[([^\]\n]+)\]|!\[([^\]\n]*)\]')
    for match in pattern.finditer(masked):
        if match.start() < consumed:
            continue
        label = match[1] if match[1] is not None else match[2]
        end = match.end()
        if end < len(masked) and masked[end] == '(':
            pos, depth, escape = end + 1, 1, False
            while pos < len(masked) and depth:
                char = masked[pos]
                if escape:
                    escape = False
                elif char == '\\':
                    escape = True
                elif char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                pos += 1
            if depth:
                raise ValueError('unterminated inline link destination')
            consumed = pos
            destination = masked[end+1:pos-1].strip()
            if destination.startswith('<'):
                close = destination.find('>')
                if close < 0:
                    raise ValueError('unterminated angle destination')
                destination = destination[1:close]
            else:
                destination = destination.split(None, 1)[0] if destination else ''
            links.append(('url', re.sub(r'\\([() ])', r'\1', destination)))
        elif end < len(masked) and masked[end] == '[':
            close = masked.find(']', end+1)
            if close < 0:
                raise ValueError('unterminated reference link')
            consumed = close + 1
            links.append(('reference', masked[end+1:close] or label))
        else:
            links.append(('shortcut', label))
    return links


def parse(text):
    anchors, links, references, warnings = set(), [], {}, []
    fence = None
    previous = None
    def add_heading(value):
        base, counter = slug(value), 0
        candidate = base
        while candidate in anchors:
            counter += 1
            candidate = f'{base}-{counter}'
        anchors.add(candidate)
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            previous = None
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            previous = None
            continue
        if line.startswith(('    ', '\t')):
            if re.search(r'!?\[.*\](?:\(|\[)', line):
                warnings.append({'line': number, 'reason': 'indented link may be code or list continuation'})
            previous = None
            continue
        container = re.match(r'^ {0,3}(?:>\s?|[-*+]\s+|\d+[.)]\s+)(.*)$', line)
        if container and re.match(r'(?:#{1,6}\s|`{3,}|~{3,}|>)', container[1]):
            warnings.append({'line': number, 'reason': 'nested heading/fence block outside supported subset'})
            previous = None
            continue
        if line.strip() == '---' and number == 1:
            warnings.append({'line': number, 'reason': 'front matter outside supported subset'})
        cleaned = re.sub(r'<a\s+(?:id|name)=["\']([^"\']+)["\']\s*>\s*</a>',
                         lambda m: anchors.add(m[1]) or '', line, flags=re.IGNORECASE)
        rendered = re.sub(r'(`+).*?\1', '', cleaned)
        if re.search(r'</?[A-Za-z][\w-]*(?:\s[^>]*|/?)>', rendered):
            warnings.append({'line': number, 'reason': 'HTML/MDX rendering outside supported subset'})
        heading = re.match(r'^ {0,3}#{1,6}\s+(.+?)(?:\s+#+\s*)?$', cleaned)
        if heading:
            add_heading(heading[1])
        elif previous and re.fullmatch(r' {0,3}(?:=+|-+)\s*', cleaned):
            add_heading(previous)
        definition = re.match(r'^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))(?:\s+.*)?$', cleaned)
        if definition:
            key = ' '.join(definition[1].split()).casefold()
            if key not in references:
                references[key] = definition[2] or definition[3]
        else:
            links.extend((number, kind, value) for kind, value in inline_links(cleaned))
        previous = cleaned.strip() if cleaned.strip() and not heading and not container else None
    if fence:
        warnings.append({'line': len(text.splitlines()), 'reason': 'unclosed fenced code block'})
    resolved = []
    for number, kind, value in links:
        if kind in {'reference', 'shortcut'}:
            key = ' '.join(value.split()).casefold()
            if key not in references:
                if kind == 'shortcut':
                    continue
                resolved.append((number, None, 'undefined-reference'))
                continue
            value = references[key]
        resolved.append((number, unescape(value), None))
    return {'anchors': anchors, 'links': resolved, 'warnings': warnings}


def audit(root: Path):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('root must be a directory')
    documents, total = {}, 0
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part in IGNORED for part in relative.parts) or path.suffix.lower() != '.md' or not path.is_file():
            continue
        real = path.resolve(strict=True)
        if not real.is_relative_to(root):
            raise ValueError('Markdown symlink escapes root')
        with path.open('rb') as handle:
            raw = handle.read(MAX_FILE+1)
        total += len(raw)
        if len(raw) > MAX_FILE or total > MAX_TOTAL or len(documents) >= MAX_FILES:
            raise ValueError('document count/byte limit exceeded')
        documents[path] = parse(raw.decode('utf-8-sig'))
    findings, warnings, checked, external = [], [], 0, 0
    for path, document in documents.items():
        source = str(path.relative_to(root))
        warnings.extend({'source': source, **w} for w in document['warnings'])
        for line, url, error in document['links']:
            row = {'source': source, 'line': line}
            if error:
                findings.append({**row, 'kind': error})
                continue
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc:
                external += 1
                continue
            checked += 1
            if parsed.query:
                warnings.append({**row, 'reason': 'local query-string link outside supported subset'})
                continue
            target = (path.parent/unquote(parsed.path)).resolve() if parsed.path else path.resolve()
            if not target.is_relative_to(root):
                findings.append({**row, 'kind': 'outside-root'})
            elif not target.is_file():
                findings.append({**row, 'kind': 'missing-file', 'target': str(target.relative_to(root))})
            elif parsed.fragment:
                if target.suffix.lower() != '.md' or target not in documents:
                    warnings.append({**row, 'reason': 'fragment target outside audited Markdown files'})
                elif unquote(parsed.fragment) not in documents[target]['anchors']:
                    findings.append({**row, 'kind': 'missing-anchor', 'target': str(target.relative_to(root)), 'fragment': unquote(parsed.fragment)})
    return {'schema': 1, 'documents': len(documents), 'checked_local_links': checked,
            'external_links_unchecked': external, 'findings': findings, 'coverage_warnings': warnings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        report = audit(args.root)
        print(json.dumps(report, indent=2, ensure_ascii=True))
        if report['coverage_warnings'] or report['documents'] == 0:
            return 2
        return int(bool(report['findings']))
    except (OSError, ValueError, RecursionError) as exc:
        print(f'doc-anchor-audit: invalid input: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
