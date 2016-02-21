import os
import sys
#from flask import Flask, request
import json

import clang_parser
import parse_markdown
import generate_site

"""
app = Flask(__name__)

@app.route('/',methods=['POST'])
def foo():
    data = json.loads(request.data)
    #print "New commit by: {}".format(data['commits'][0]['author']['name'])
    return "OK"

"""

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

    of_root = os.path.abspath(sys.argv[1])
    markdown_root = os.path.abspath(sys.argv[2])
    site_output = os.path.abspath(sys.argv[3])

    if sys.argv[4]:
        json_data_root = os.path.abspath(sys.argv[4])
    else:
        json_data_root = os.path.join(dir, '../_json_data')

    if not os.path.exists(of_root):
        raise Exception("openframeworks path not found, must be supplied as first argument")

    if not os.path.exists(markdown_root):
        raise Exception("markdown path not found, must be supplied as second argument")

    run(of_root, markdown_root, json_data_root, site_output)
    #app.run()