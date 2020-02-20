"""
template.py

Takes and environment template and injects values into it from the command line.

Usage:
  template.py <template_file> <replacements>
  template.py - <replacements>
  template.py (-h | --help)

Options:
  -h --help   Show this screen.

"""
import sys
import json
from docopt import docopt
from jinja2 import Template


def replace(template, replacements):
    return Template(template).render(**replacements)


def main(args):
    if args['<template_file>']:
        with open(args['<template_file>'], 'r') as template_file:
            template = template_file.read()
    else:
        template = sys.stdin.read()

    replacements = json.loads(args['<replacements>'])

    sys.stdout.write(replace(template, replacements))
    sys.stdout.close()


if __name__ == "__main__":
    main(docopt(__doc__, version='1'))
