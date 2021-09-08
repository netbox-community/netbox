#!/usr/bin/env bash

# This script verifies the integrity of *bundled* static assets by re-running the bundling process
# and checking for changed files. Because bundle output should not change given the same source
# input, the bundle process shouldn't produce any changes. If they do, it's an indication that
# the dist files have been altered, or that dist files were not committed. In either case, tests
# should fail.

PROJECT_STATIC="$PWD/netbox/project-static"
DIST="$PROJECT_STATIC/dist/"

# Bundle static assets.
bundle() {
    echo "Bundling static assets..."
    yarn --cwd $PROJECT_STATIC bundle >/dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo "Error bundling static assets"
        exit 1
    fi
}

# See if any files have changed.
check_dist() {
    local diff=$(git --no-pager diff $DIST)
    if [[ $diff != "" ]]; then
        local SHA=$(git rev-parse HEAD)
        echo "Commit '$SHA' produced different static assets than were committed"
        exit 1
    fi
}

bundle
check_dist

if [[ $? = 0 ]]; then
    echo "Static asset check passed"
    exit 0
else
    echo "Error checking static asset integrity"
    exit 1
fi
