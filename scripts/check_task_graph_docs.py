"""Validate local references, bilingual coverage and JavaScript syntax."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links = [], []
        self.headings = 0
        self.languages = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        self.headings += tag == 'h1'
        if 'data-doc-lang' in attrs:
            self.languages.add(attrs['data-doc-lang'])
        if tag == 'img':
            assert attrs.get('alt'), 'Missing image alternative'
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])


def main():
    content = (ROOT / 'task-graph.html').read_text()
    doc = Document()
    doc.feed(content)
    assert doc.headings == 1
    assert len(doc.ids) == len(set(doc.ids)), 'Duplicate anchor'
    assert doc.languages == {'en', 'zh'}
    for link in doc.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        if url.path:
            assert (ROOT / unquote(url.path)).is_file(), f'Missing file: {link}'
        elif url.fragment:
            assert url.fragment in doc.ids, f'Missing anchor: {link}'
    for lang in ('en', 'zh'):
        source = (ROOT / f'docs/architecture/session-task-attempt.{lang}.md').read_text()
        headings = re.findall(r'^## (.+)$', source, re.M)
        assert len(headings) == 13
        for heading in headings:
            assert heading in content, f'Missing translated section: {heading}'
    assert 'href="task-graph.html"' in (ROOT / 'wiki.html').read_text()
    translations = (ROOT / 'i18n.js').read_text()
    for key in ('tg.title', 'tg.entry', 'tg.description'):
        assert translations.count(f'"{key}":') == 2, f'Missing translation: {key}'
    for script in ('i18n.js', 'wiki.js'):
        subprocess.run(['node', '--check', str(ROOT / script)], check=True)
    print('PASS: links, anchors, image alternatives, bilingual sections, navigation and JavaScript syntax')


if __name__ == '__main__':
    main()
