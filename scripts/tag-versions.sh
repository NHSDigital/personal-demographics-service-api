#!/bin/bash

set -euo pipefail

VERSION=$(poetry run python scripts/calculate_version.py)


git config credential.helper 'cache --timeout 120'
git config user.email "<email>"
git config user.name "Marvin (Automated)"
git tag "$VERSION"
git push -q https://${GITHUB_ACCESS_TOKEN}@github.com/NHSDigital/personal-demographics-service-api "$VERSION" > /dev/null 2>&1
