#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/opt/homebrew/opt/ruby@3.3/bin:/opt/homebrew/lib/ruby/gems/3.3.0/bin:/opt/homebrew/opt/node@22/bin:$PATH"
# Keep verification separate from a running Jekyll preview.
export SITE_DIR="${SITE_DIR:-.check-site}"
export JEKYLL_ENV=production
export BUNDLE_FROZEN=true
bundle _2.4.17_ exec jekyll build --destination "$SITE_DIR"
npm run check
npm test
