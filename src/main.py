import os
import sys
import json

from clang_parser import clang_parser
from markdown_parser import parse_markdown
from site_generator import generate_site

def run(of_root, markdown_root, json_data_root, site_output):
    print "Run clang parser"
    clang_parser.run(of_root, json_data_root)

    print "Run markdown parser"
    parse_markdown.run(markdown_root, json_data_root)

    print "Run generate site"
    generator = generate_site.SiteGenerator()
    generator.run(markdown_root, json_data_root, site_output)
    print "Done generating site"


if __name__ == '__main__':
    dir = os.path.dirname(__file__)

    of_root = os.path.abspath(os.getenv('OF_ROOT', ''))
    markdown_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_ROOT', ''))
    site_output = os.path.abspath(os.getenv('OF_DOCUMENTATION_SITE_OUTPUT', './_site'))
    json_data_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_JSON_DIR', './_json_data'))

    if len(of_root) == 0 or not os.path.exists(of_root):
        raise Exception("openframeworks path not found, must be supplied as first argument")

    if len(markdown_root) == 0 or not os.path.exists(markdown_root):
        raise Exception("markdown path not found, must be supplied as second argument "+markdown_root)

    run(of_root, markdown_root, json_data_root, os.path.join(site_output,'latest'))
