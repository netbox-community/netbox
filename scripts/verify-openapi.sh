#!/usr/bin/env bash

# This script checks for differences between the generated OpenAPI schema and the static definition
# saved at contrib/openapi.json. If the two are not identical, the script returns an error.

PROJECT_ROOT="$PWD"
CMD="python $PROJECT_ROOT/netbox/manage.py spectacular --format openapi-json"
SCHEMA_FILE="$PROJECT_ROOT/contrib/openapi.json"

# Generate the OpenAPI schema & save it to a temporary file
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT
eval "$CMD > $TEMP_FILE"

# Run a diff between the original & generated schemas
if diff -u "$SCHEMA_FILE" "$TEMP_FILE"; then
    echo "✅ No changes found."
    exit 0
else
    echo "❌ Change(s) to OpenAPI schema detected."
    exit 1
fi
