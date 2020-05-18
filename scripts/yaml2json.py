#!/usr/bin/env python3
"""
yaml2json.py

Takes yaml on stdin and writes json on stdout, converting dates correctly.
"""
import sys
import json
import datetime
import yaml


def date_converter(obj):
    """Date and datetime converter to correctly render dates in json"""
    if isinstance(obj, datetime.datetime):
        return obj.replace(tzinfo=datetime.timezone.utc).isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj


def main():
    """Main entrypoint"""
    data = yaml.load(Loader=yaml.FullLoader, stream=sys.stdin.read())
    sys.stdout.write(json.dumps(data, default=date_converter, indent=2))
    sys.stdout.close()


if __name__ == "__main__":
    main()
