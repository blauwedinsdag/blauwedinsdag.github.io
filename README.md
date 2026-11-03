# Blauwe Dinsdag

Jekyll / Minima website for Blauwe Dinsdag, published at https://blauwedinsdag.com.

## Local preview

Double-click **Blauwe Dinsdag Preview.app** on the Desktop. It opens Terminal,
starts Jekyll, and opens http://127.0.0.1:4000 once ready. If the preview is
already running, the app opens it without starting another server.

Keep Terminal open while previewing. Press **Control+C** in the preview's
Terminal window to stop. Content changes rebuild automatically with live reload;
restart the preview after changing `_config.yml`.

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

GitHub Pages builds the repository root on `main`. Commit and push changes to
that branch to publish. Local preview does not publish anything; do not commit
the generated `_site/` folder or installed gems.

## Media and metadata

Use the build-time includes for new players; cassette playback works without
JavaScript and includes a direct file link:

```liquid
{% include audio.html src="/audio/01 Warm.mp3" title="Warm" %}
{% include spotify.html type="album" id="0hpriflp4Fn6A1JMz7HWQl" title="Blauwe Dinsdag — Schreeuwende Snaren" %}
```

Spotify supports optional `height`, `width`, and `theme` parameters. Audio uses
`preload="none"` to avoid loading recordings before a visitor starts playback.
Put players inside a `<div>` rather than a `<p>` when grouping them.

Images should have descriptive Dutch `alt` text, intrinsic pixel `width` and
`height`, and `height: auto` when resized. Keep the heading levels sequential.

The default sharing image is configured in `_config.yml`. Override it in a
page or post's front matter when a more specific image is available:

```yaml
image:
  path: /images/schreeuwende_snaren.jpeg
  alt: Albumhoes van Schreeuwende Snaren
```
