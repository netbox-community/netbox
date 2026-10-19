#!/usr/bin/env bash

# This script verifies the integrity of *bundled* static assets by re-running the bundling process
# and checking for changed, added, or deleted files. Because bundle output should not change given
# the same source input, the bundle process shouldn't produce any changes. If it does, it's an
# indication that the dist files have been altered, or that dist files were not committed. In
# either case, tests should fail.

set -euo pipefail

cd "$(dirname "$0")/../netbox/project-static"

echo "Bundling static assets..."
if ! npm run --silent build; then
    echo "Error bundling static assets"
    exit 1
fi

# See if any files have been changed, added, or deleted.
if [[ -n "$(git status --porcelain -- dist)" ]]; then
    git status --short -- dist
    echo "Commit '$(git rev-parse HEAD)' produced different static assets than were committed"
    echo "Run 'npm run build' in netbox/project-static/ and commit the contents of dist/"
    exit 1
fi

echo "Static asset check passed"
