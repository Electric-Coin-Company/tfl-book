#!/bin/bash
#
# Any page which contains `\[Incomplete Placeholder\]` should have
# `(TBD)` in the table of contents.
#
# This script checks this consistency.

# Move to src dir:
cd "$(dirname "$(readlink -f "$0")")/../src"

DATADIR="$(mktemp --directory)"
TBD_PATHS="${DATADIR}/tbds"
INCOMPLETE_PATHS="${DATADIR}/incompletes"

grep '(TBD)' ./SUMMARY.md | sed 's|^.*(\./||; s|)$||' | sort > "$TBD_PATHS"
grep -Hr 'Incomplete Placeholder' | sed 's|:.*$||' | sort > "$INCOMPLETE_PATHS"

exec diff -u "$TBD_PATHS" "$INCOMPLETE_PATHS"
