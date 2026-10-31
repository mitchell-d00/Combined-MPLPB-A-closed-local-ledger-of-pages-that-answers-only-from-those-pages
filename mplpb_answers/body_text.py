"""Versioned body projection for citations; headings/active metadata are excluded."""
from html.parser import HTMLParser
import re

VERSION = 'body-text-no-headings-v1'


def body_text(html):
    class Body(HTMLParser):
        SKIP = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'script', 'style', 'head', 'title', 'noscript'}
        BLOCK = {'p', 'div', 'li', 'tr', 'br', 'pre', 'section', 'ul', 'ol', 'table'}
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts, self.blocked = [], []
        def handle_starttag(self, tag, attrs):
            if tag in self.SKIP:
                self.blocked.append(tag)
            elif not self.blocked and tag in self.BLOCK:
                self.parts.append('\n')
        def handle_endtag(self, tag):
            if tag in self.blocked:
                index = len(self.blocked)-1-self.blocked[::-1].index(tag)
                del self.blocked[index:]
                if not self.blocked:
                    self.parts.append('\n')
            elif not self.blocked and tag in self.BLOCK:
                self.parts.append('\n')
        def handle_data(self, text):
            if not self.blocked:
                self.parts.append(text)
    parser = Body(); parser.feed(html); parser.close()
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in ''.join(parser.parts).splitlines()]
    return '\n'.join(line for line in lines if line)
