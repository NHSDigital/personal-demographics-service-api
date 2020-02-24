"""
template.py

Takes a jinja2 template and injects values into it from the command line.

Can operate with a template file or from stdin. Replacements can be supplied as an argument in JSON format or from env.

Usage:
  template.py [<replacements>] [-f <path> | --file=<path>] [-e | --env]
  template.py - [<replacements>] [-e | --env]
  template.py (-h | --help)

Options:
  -h --help                 Show this screen.
  -f <path> --file=<path>   Template from file at path.
  -e --env                  Replace from environment variables instead of JSON argument.
"""
import os
import sys
import json
from docopt import docopt
from jinja2 import Template


def replace(template, replacements):
    return Template(template).render(**replacements)


def main(args):
    template = ""
    if args['--file']:
        with open(args['--file'], 'r') as template_file:
            template = template_file.read()
    else:
        template = sys.stdin.read()

    replacements = {}
    if args['<replacements>']:
        replacements = json.loads(args['<replacements>'])
    elif args['--env']:
        replacements = os.environ

    sys.stdout.write(replace(template, replacements))
    sys.stdout.close()


if __name__ == "__main__":
    main(docopt(__doc__, version='1'))
