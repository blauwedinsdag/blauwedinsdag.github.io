# Blauwe Dinsdag

Jekyll / Minima website for Blauwe Dinsdag, published at https://blauwedinsdag.com.

## Local preview

Double-click **Blauwe Dinsdag Preview.app** on the Desktop. It opens Terminal,
starts Jekyll, and opens http://127.0.0.1:4000 once ready. If the preview is
already running, the app opens it without starting another server.

Keep Terminal open while previewing. Press **Control+C** in the preview's
Terminal window to stop. Content changes rebuild automatically with live reload;
restart the preview after changing `_config.yml`.

The local preview includes future-dated posts so you can review them before publication.

To launch directly from this folder:

```sh
bash scripts/preview.sh
```

The launcher uses Homebrew Ruby 3.3 directly; no shell configuration is needed.
Dependencies are installed in ignored `vendor/bundle/`, with the local Bundler
settings in ignored `.bundle/`.

### Set up a new Apple Silicon Mac

With Homebrew and Apple Command Line Tools installed:

```sh
brew install ruby@3.3
export PATH="/opt/homebrew/opt/ruby@3.3/bin:/opt/homebrew/lib/ruby/gems/3.3.0/bin:$PATH"
gem install bundler -v 2.4.17 --no-document
bundle _2.4.17_ config set --local path vendor/bundle
bundle _2.4.17_ install
```

The Desktop app's source is `scripts/preview.applescript`. If the repository moves,
update `repositoryPath` in that file, then compile it (choose a new output name
if an app with that name already exists):

```sh
osacompile -o "$HOME/Desktop/Blauwe Dinsdag Preview.app" scripts/preview.applescript
```

## Publish revisions

The **Website checks and deployment** GitHub Actions workflow builds `main` with
the Ruby version in `.ruby-version`, Bundler 2.4.17, and `Gemfile.lock`. It runs
HTML, YAML, local-link, media, desktop/mobile, and axe accessibility checks before
deploying. Pull requests run the same checks without publishing.

GitHub repository **Settings → Pages → Source** must be **GitHub Actions** for
this workflow. The custom domain remains `blauwedinsdag.com`.

Commit and push to `main` to publish. Include the generated `images/optimized/`
files and `_data/images.json` when updating images. Do not commit `_site/`,
`.check-site/`, test reports, or installed dependencies. Local preview never publishes.

The separate **External link report** workflow checks public outbound links
weekly and on demand. Network failures or bot protection may need manual review;
these reports do not block publication.

## Run the checks locally

One-time test setup (the normal Desktop preview does not need Node):

```sh
brew install node@22
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"
npm ci
npm run browsers
```

Then run:

```sh
bash scripts/check.sh
```

Checks build into `.check-site/`, separate from a running preview. Chromium tests
cover desktop and mobile layouts, keyboard navigation, responsive image loading,
and cassette players without JavaScript. External players are blocked during
tests; their frame titles and source markup are checked, but their own interfaces
and network availability are outside these tests. Automated axe checks cover
detectable WCAG A/AA issues and do not replace manual accessibility review.

Reports appear in ignored `playwright-report/` and `test-results/`. For an optional
network-dependent link report after running the checks:

```sh
SITE_DIR=.check-site npm run check:external
```

## Media and metadata

Use the build-time includes for new players; cassette playback works without
JavaScript and includes a direct file link:

```liquid
{% include audio.html src="/audio/01 Warm.mp3" title="Warm" %}
{% include spotify.html type="album" id="0hpriflp4Fn6A1JMz7HWQl" title="Blauwe Dinsdag — Schreeuwende Snaren" %}
```

Spotify supports optional `height` and `theme` parameters. Its width is responsive
through the shared stylesheet. Audio uses
`preload="none"` to avoid loading recordings before a visitor starts playback.
Put players inside a `<div>` rather than a `<p>` when grouping them.

Use the image include for photos and scans:

```liquid
{% include image.html src="/images/basementtapes.jpeg" alt="Historische groepsfoto in de repetitieruimte" %}
```

It supplies dimensions, WebP `srcset`, an original-file fallback, and lazy loading.
Use `loading="eager"` for the first visible images. `sizes` can describe the image's
display width. Photo rows use `media-group photo-grid photo-grid--2` (or `--3`,
`--4`); add `portraits` to keep two portraits per row on small screens. Other
galleries become a single column on the smallest screens. Styles live in
`assets/site.css`; article lists share `_includes/post-list.html`.

After adding or replacing originals, regenerate the derivatives:

```sh
npm run images
```

This leaves the originals intact and generates automatically oriented WebP sizes
up to 1440 pixels wide. Commit the results together with `_data/images.json`.
The checks detect changed originals whose variants have not been regenerated.
Keep image descriptions in Dutch and heading levels sequential.

The default sharing image is configured in `_config.yml`. Override it in a
page or post's front matter when a more specific image is available:

```yaml
image:
  path: /images/schreeuwende_snaren.jpeg
  alt: Albumhoes van Schreeuwende Snaren
```
