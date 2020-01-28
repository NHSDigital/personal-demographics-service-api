#!/bin/bash
set -euo pipefail

LICENSES=$(poetry run pip-licenses)
INCOMPATIBLE_LIBS=$(echo "$LICENSES" | grep 'GPL' || true)

if [[ -z $INCOMPATIBLE_LIBS ]]; then
    exit 0
else
    echo "The following libraries were found which are not compatible with this project's license:"
    echo "$INCOMPATIBLE_LIBS"
    exit 1
fi
