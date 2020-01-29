#!/usr/bin/env python3
import sys
import json
from calculate_version import calculate_version


data = json.loads(sys.stdin.read())
data['info']['version'] = str(calculate_version())
sys.stdout.write(json.dumps(data, indent=2))
sys.stdout.close()
