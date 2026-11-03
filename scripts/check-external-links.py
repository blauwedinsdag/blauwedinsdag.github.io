"""Network-dependent checks, run separately from the deployment gate."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urlsplit
from urllib.request import Request, urlopen

urls = set()


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        url = urlsplit(href)
        if url.scheme in ("http", "https") and url.hostname != "blauwedinsdag.com":
            urls.add(urldefrag(href)[0])


for path in Path(os.environ.get("SITE_DIR", "_site")).rglob("*.html"):
    Links().feed(path.read_text())
if not urls:
    sys.exit("No external links found. Build the site first.")


def check(url):
    for method in ("HEAD", "GET"):
        try:
            request = Request(url, method=method, headers={"User-Agent": "BlauweDinsdag-LinkCheck/1.0"})
            with urlopen(request, timeout=12) as response:
                return url, None
        except HTTPError as error:
            if method == "HEAD":
                continue
            return url, f"HTTP {error.code} (may be bot protection)"
        except (URLError, TimeoutError, OSError) as error:
            return url, str(error)


with ThreadPoolExecutor(max_workers=4) as executor:
    failures = [(url, reason) for url, reason in executor.map(check, sorted(urls)) if reason]
for url, reason in failures:
    print(f"{reason}: {url}")
print(f"Checked {len(urls)} external links; {len(failures)} need review.")
sys.exit(bool(failures))
