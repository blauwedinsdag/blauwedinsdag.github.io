#!/bin/bash
set -eu

# Explicit paths also work when launched by Finder, without shell setup.
export PATH="/opt/homebrew/opt/ruby@3.3/bin:/opt/homebrew/lib/ruby/gems/3.3.0/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd "$(dirname "$0")/.."
preview_url="http://127.0.0.1:4000"

if /usr/bin/curl --silent --fail --max-time 2 "$preview_url" | /usr/bin/grep -q '<title>.*Blauwe Dinsdag'; then
  /usr/bin/open "$preview_url"
  exit 0
fi

bundle _2.4.17_ check
printf '\033]0;Blauwe Dinsdag Preview\007'
printf 'Starting Blauwe Dinsdag preview. Press Control+C here to stop.\n'

bundle _2.4.17_ exec jekyll serve --future --host 127.0.0.1 --port 4000 --livereload &
server_pid=$!
opener_pid=""
cleanup() {
  trap - EXIT INT TERM
  if [ -n "$opener_pid" ]; then kill "$opener_pid" 2>/dev/null || true; fi
  kill "$server_pid" 2>/dev/null || true
  wait "$server_pid" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

(
  for attempt in {1..120}; do
    kill -0 "$server_pid" 2>/dev/null || exit 0
    if /usr/bin/curl --silent --fail --max-time 1 "$preview_url" | /usr/bin/grep -q '<title>.*Blauwe Dinsdag'; then
      /usr/bin/open "$preview_url"
      exit 0
    fi
    sleep 0.5
  done
  printf 'Preview is taking longer than expected. Check the Jekyll output above.\n'
) &
opener_pid=$!
wait "$server_pid"
