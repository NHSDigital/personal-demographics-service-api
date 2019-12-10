#!/usr/bin/env python3
import sys
import yaml
import json
import datetime


def date_converter(o):
    if isinstance(o, datetime.datetime):
        return o.replace(tzinfo=datetime.timezone.utc).isoformat()
    elif isinstance(o, datetime.date):
        return o.isoformat()


data = yaml.load(Loader=yaml.FullLoader, stream=sys.stdin.read())
sys.stdout.write(json.dumps(data, default=date_converter, indent=2))
sys.stdout.close()
