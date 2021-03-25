import glob2
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys


def parsefile(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)


for file in glob2.glob('./proxies/**/*.xml'):
    try:
        parsefile(file)
    except Exception as e:
        print("%s is NOT well-formed! %s" % (file, e))
        sys.exit(1)
