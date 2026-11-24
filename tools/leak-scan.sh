#!/usr/bin/env bash
# Scan for private/company details before publishing. Exit 1 on any hit.
# Usage: tools/leak-scan.sh [path...]   (default: skills/)
# Add your own terms to tools/leak-terms.txt (one regex per line, gitignored).
set -u
paths=("${@:-skills}")
pat='/Users/[a-z]|\b(AUTO|CS|BE|EP|DEVOPS|QA)-[0-9]+\b|gitlab\.com/[a-z]|\bC0[0-9A-Z]{8,}\b|claude\.ai/(code/)?artifact|Desktop/Tasks|@[a-z0-9.-]+\.(com|net|io)\b'
extra=""; [ -f "$(dirname "$0")/leak-terms.txt" ] && extra="$(dirname "$0")/leak-terms.txt"
hits=$(grep -rInE "$pat" "${paths[@]}" ; [ -n "$extra" ] && grep -rInEf "$extra" "${paths[@]}")
if [ -n "$hits" ]; then echo "$hits"; echo "LEAK-SCAN: FAIL ($(echo "$hits" | wc -l | tr -d ' ') hits)"; exit 1; fi
echo "LEAK-SCAN: PASS"
