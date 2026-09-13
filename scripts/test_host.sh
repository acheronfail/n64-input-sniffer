#!/bin/sh
# Run the actual firmware helpers on the host, without an ESP32 or PlatformIO.
set -eu
cd "$(dirname "$0")/.."
test_dir=$(mktemp -d "${TMPDIR:-/tmp}/n64-host-tests.XXXXXX")
trap 'rm -rf "$test_dir"' EXIT HUP INT TERM
for source in test/*_test.cpp; do
  name=$(basename "$source" .cpp)
  "${CXX:-c++}" -std=c++11 -Wall -Wextra -Werror -Iinclude "$source" -o "$test_dir/$name"
  "$test_dir/$name"
done
