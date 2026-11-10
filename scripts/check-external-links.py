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
                return url, None, False
        except HTTPError as error:
            if method == "HEAD":
                continue
            needs_review = error.code in (401, 403, 429)
            reason = f"HTTP {error.code}"
            if needs_review:
                reason += " (access denied or rate limited; review manually)"
            return url, reason, needs_review
        except (URLError, TimeoutError, OSError) as error:
            return url, str(error), False


with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(check, sorted(urls)))
failures = [(url, reason) for url, reason, review in results if reason and not review]
reviews = [(url, reason) for url, reason, review in results if review]
for level, findings in (("error", failures), ("warning", reviews)):
    for url, reason in findings:
        message = f"{reason}: {url}"
        if os.environ.get("GITHUB_ACTIONS") == "true":
            # Escape workflow-command data, including text from remote servers.
            message = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::{level}::{message}")
        else:
            print(f"{level}: {message}")
print(f"Checked {len(urls)} external links; {len(failures)} failed; {len(reviews)} need manual review.")
sys.exit(bool(failures))
