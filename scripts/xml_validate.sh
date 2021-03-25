#!/bin/bash
set -euo pipefail


if [poetry run python scripts/xml_validator.py -eq 0]; then
    echo "No XML validation errors!"
    exit 0
else
    echo "XML validation errors"
    exit 1
fi