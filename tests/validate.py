"""Offline validation: python3 tests/validate.py (no Firebase login/deploy)."""
import json
from html.parser import HTMLParser
from pathlib import Path
root = Path(__file__).resolve().parents[1]
assert json.loads((root / "firebase.json").read_text())["hosting"]["public"] == "public"
class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.seen = []
        self.doctype = False
    def handle_decl(self, decl):
        assert decl.lower() == "doctype html"
        self.doctype = True
    def handle_starttag(self, tag, attrs):
        assert "<" not in tag
        expected = {"html": [], "head": ["html"], "body": ["html"], "h1": ["html", "body"]}
        if tag in expected:
            assert self.stack == expected[tag], (tag, self.stack)
        self.seen.append(tag)
        if tag not in {"meta", "link", "br", "img", "input"}:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        assert self.stack.pop() == tag
parser = Structure()
parser.feed((root / "public/index.html").read_text())
assert parser.doctype and not parser.stack
assert all(parser.seen.count(tag) == 1 for tag in ["html", "head", "body", "h1"])
print("PASS: strict JSON and HTML token/nesting validation")
