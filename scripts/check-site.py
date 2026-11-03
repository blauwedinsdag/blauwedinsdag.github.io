"""Validate generated local links, fragments, media, and responsive image assets."""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(os.environ.get("SITE_DIR", "_site")).resolve()
errors = []
counts = Counter()
documents = {}


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.ids = set()
        self.targets = []
        self.meta = {}
        self.heading = 0
        self.main = False
        self.h1 = 0

    def error(self, message):
        errors.append(f"{self.path.relative_to(ROOT)}: {message}")

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.error(f"Duplicate ID: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "main":
            self.main = True
        if self.main and tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.h1 += level == 1
            if level > self.heading + 1:
                self.error(f"Heading jumps from h{self.heading} to {tag}")
            self.heading = level
        if tag == "meta":
            key = attrs.get("property", attrs.get("name"))
            self.meta.setdefault(key, []).append(attrs.get("content"))
        if tag == "img":
            counts["images"] += 1
            if not attrs.get("alt"):
                self.error("Image has no description")
            if not all(attrs.get(key, "").isdigit() and int(attrs[key]) > 0 for key in ("width", "height")):
                self.error("Image has no intrinsic dimensions")
            if attrs.get("loading") not in ("lazy", "eager"):
                self.error("Image has no loading policy")
        if tag == "iframe":
            counts["embeds"] += 1
            if not attrs.get("title"):
                self.error("Frame has no title")
        if tag == "audio":
            counts["audio players"] += 1
            if "controls" not in attrs or not attrs.get("aria-label") or attrs.get("preload") != "none":
                self.error("Audio needs controls, a label, and preload=none")
        for key in ("href", "src"):
            if attrs.get(key):
                self.targets.append(attrs[key])
        if attrs.get("srcset"):
            self.targets.extend(candidate.strip().split()[0] for candidate in attrs["srcset"].split(","))

    def handle_endtag(self, tag):
        if tag == "main":
            self.main = False


for path in sorted(ROOT.rglob("*.html")):
    doc = Document(path)
    doc.feed(path.read_text())
    documents[path] = doc
    if doc.h1 != 1:
        doc.error(f"Expected one main heading, found {doc.h1}")
    if doc.meta.get("og:locale") != ["nl_NL"]:
        doc.error("Expected Dutch metadata")
    if len(doc.meta.get("og:image", [])) != 1:
        doc.error("Expected one sharing image")
    if doc.meta.get("og:image") != doc.meta.get("twitter:image"):
        doc.error("Inconsistent sharing images")
    if "#main-content" not in doc.targets:
        doc.error("Missing skip link")
    doc.targets.extend(doc.meta.get("og:image", []))

if not documents:
    errors.append("No generated HTML found. Run bundle exec jekyll build first.")

for doc in documents.values():
    for target in doc.targets:
        url = urlsplit(target)
        if url.scheme not in ("", "http", "https") or url.netloc not in ("", "blauwedinsdag.com"):
            continue
        path = unquote(url.path)
        destination = ROOT / path.lstrip("/") if path.startswith("/") or url.netloc else doc.path.parent / path
        if not path:
            destination = doc.path
        destination = destination.resolve()
        if destination.is_dir():
            destination /= "index.html"
        if not destination.is_relative_to(ROOT) or not destination.is_file():
            doc.error(f"Missing local file: {target}")
        elif url.fragment and destination in documents and unquote(url.fragment) not in documents[destination].ids:
            doc.error(f"Missing fragment: {target}")

manifest = json.loads(Path("_data/images.json").read_text())
for source, image in manifest.items():
    if sha256(Path(source.lstrip("/")).read_bytes()).hexdigest() != image["sha256"]:
        errors.append(f"Image changed: {source}; regenerate with npm run images")
    for variant in image["variants"]:
        if not (ROOT / variant["url"].lstrip("/")).is_file():
            errors.append(f"Missing responsive image: {variant['url']}")

for name in ("scripts", "node_modules", "tests", "vendor", ".check-site", "package.json", "package-lock.json", "playwright.config.mjs", "README.md", "Gemfile", "Gemfile.lock"):
    if (ROOT / name).exists():
        errors.append(f"Build contains tooling: {name}")

try:
    ET.parse(ROOT / "feed.xml")
except (ET.ParseError, OSError) as error:
    errors.append(f"Invalid feed: {error}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Local checks passed: {len(documents)} pages; " + ", ".join(f"{value} {key}" for key, value in counts.items()))
