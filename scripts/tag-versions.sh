#!/bin/bash

set -euo pipefail

VERSION=$(poetry run python scripts/calculate_version.py)
git tag "$VERSION"
git push origin "$VERSION"
