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
        print("\x1b[0;30;41m" + f"{file} is NOT well-formed! {e}" + "\x1b[0m" )
        sys.exit(1)

sys.exit(0)
