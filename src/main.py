#!/usr/bin/python
"""
This will run the clang parser on openFrameworks,
and generate a json file for each file in openframeworks

These JSON files can then be used by the site generator to create the site
"""

import os
import sys
import shutil

from clang.cindex import CursorKind

import json_file
import clang_utils
import utils

import documentation_reference
from documentation_class import DocClass
from documentation_function import DocFunction

""" Get path of openframeworks from argv """
of_root = sys.argv[1]
of_source = os.path.join(of_root, "libs/openFrameworks")

""" json output dir """
dir = os.path.dirname(__file__)
outdir = os.path.join(dir,'../_json_documentation/')

of_addons = os.path.join(of_root, "addons")
official_addons = [
    "ofxAccelerometer",
    "ofxAndroid",
    "ofxAssimpModelLoader",
    "ofxEmscripten",
    "ofxGui",
    "ofxNetwork",
    "ofxOpenCv",
    "ofxOsc",
    "ofxSvg",
    "ofxThreadedImageLoader",
    "ofxXmlSettings",
]
currentversion = "0.9.0"
alternatives = {
    'size_t': ['int', 'unsigned int', 'long', 'unsigned long'],
    'filesystem::path': ['string'],
    'ofIndexType': ['int', 'unsigned int', 'long'],
    'unsigned long': ['int', 'unsigned int', 'long'],
    'unsigned long long': ['int', 'unsigned int', 'long'],
}


def add_class(data, offilename, folder):
    if offilename not in json_data:
        json_data[offilename] = {
            "name": offilename,
            "folder":folder,
            "classes": [],
            "functions": []
        }
    json_data[offilename]['classes'].append(data)


def add_function(data, offilename, folder):
    if offilename not in json_data:
        json_data[offilename] = {
            "name": offilename,
            "folder":folder,
            "classes": [],
            "functions": []
        }
    json_data[offilename]['functions'].append(data)


def parse_file_child(child):
    if child.spelling.find('of') == 0:
        offilename = utils.filenameFromClangChild(child)

        if utils.is_class(child):
            i = 0
            for c in child.get_children():
                if utils.is_variable(c) or utils.is_method(c) or c.kind == CursorKind.CXX_BASE_SPECIFIER:
                    i += 1
            if i > 0 and child.spelling not in visited_classes:
                new_class = DocClass(child)
                add_class(new_class.serialize(), offilename, new_class.folder)
                visited_classes.append(child.spelling)

        if utils.is_function(child):
            if child.spelling not in visited_function and offilename != "ofMain":
                visited_function.append(child.spelling)
                new_func = DocFunction(child, None)
                add_function(new_func.serialize(), offilename, new_func.folder)


def parse_folder(root, files, is_addon=False):
    for name in files:
        filepath = os.path.join(root, name)

        if name.split('.')[0] not in json_data.keys() and name.find('of') == 0 and os.path.splitext(name)[1] == '.h':
            tu = clang_utils.get_tu_from_file(filepath, of_root)
            for child in tu.cursor.get_children():
                parse_file_child(child)


""" main """
dir_count = 0
file_count = 0
visited_classes = []
visited_function = []
missing_functions = []
missing_methods = []
missing_vars = []
new_classes = []
new_functions = []
new_vars = []
new_methods = []


if os.path.exists(outdir):
    shutil.rmtree(outdir)
os.makedirs(outdir)


json_data = {}
for root, dirs, files in os.walk(of_source):
    dir_count += 1
    print root, files
    parse_folder(root, files, False)
# parse_folder("/Users/jonas/Development/openframeworks/openframeworks/libs/openFrameworks/gl/", ["ofTexture.h"], False)

"""
for addon in official_addons:
    for root, dirs, files in os.walk(os.path.join(of_addons, addon, "src")):
        dir_count += 1
        file_count += parse_folder(root, files, True)
"""
for key in json_data:
    json_file.save(outdir, key, json_data[key])

documentation_reference.save(outdir)

if len(new_functions) > 0:
    print "added " + str(len(new_functions)) + " new functions:"
    for f in new_functions:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  to " + f.functionsfile

if len(missing_functions) > 0:
    print "removed " + str(len(missing_functions)) + " functions"
    for f in missing_functions:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  from " + f.functionsfile

if len(new_methods) > 0:
    print "added " + str(len(new_methods)) + " new methods:"
    for f in new_methods:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  to " + f.clazz

if len(missing_methods) > 0:
    print "removed " + str(len(missing_methods)) + " methods"
    for f in missing_methods:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  from " + f.clazz

if len(new_vars) > 0:
    print "added " + str(len(new_vars)) + " new vars:"
    for v in new_vars:
        print "\t- " + v.name + "  to " + v.clazz

if len(missing_vars) > 0:
    print "removed " + str(len(missing_vars))
    for v in missing_vars:
        print "\t- " + v.name + "  from " + v.clazz