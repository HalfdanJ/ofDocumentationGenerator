"""
This will run the clang parser on openFrameworks,
and generate a json file for each file in openframeworks

These JSON files can then be used by the site generator to create the site
"""

import os
import shutil

from clang.cindex import CursorKind

from utils import json_file
#from ..utils import json_file

import clang_utils

import clang_reference
from clang_class import DocClass
from clang_function import DocFunction
from clang_enum import DocEnum
from clang_typedef import DocTypedef

dir_count = 0
file_count = 0
visited_classes = []
visited_enums = []
visited_function = []
visited_typedefs = []

missing_functions = []
missing_methods = []
missing_vars = []
new_classes = []
new_functions = []
new_vars = []
new_methods = []
json_data = {}


"""
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
"""

def add_file(offilename, folder):
    json_data[offilename] = {
        "name": offilename,
        "filename": offilename+'.h',
        "type": 'file',
        "folder":folder,
        "classes": [],
        "functions": [],
        "enums":[],
        "typedefs":[]
    }

def add_class(data, offilename, folder):
    """ Add class to json data output """
    if offilename not in json_data:
        add_file(offilename, folder)
    json_data[offilename]['classes'].append(data)

def add_function(data, offilename, folder):
    """ Add function to json data output """
    if offilename not in json_data:
        add_file(offilename, folder)
    json_data[offilename]['functions'].append(data)

def add_enum(data, offilename, folder):
    """ Add enum to json data output """
    if offilename not in json_data:
        add_file(offilename, folder)
    json_data[offilename]['enums'].append(data)

def add_typedef(data, offilename):
    """ Add typedef to json data output """
    if offilename not in json_data:
        add_file(offilename, data['folder'])
    json_data[offilename]['typedefs'].append(data)

def parse_file_child(child):
    if child.spelling.startswith('of'):
        offilename = clang_utils.filenameFromClangChild(child)

        if clang_utils.is_class(child):
            i = 0
            for c in child.get_children():
                if clang_utils.is_variable(c) or clang_utils.is_method(c) or c.kind == CursorKind.CXX_BASE_SPECIFIER:
                    i += 1
            if i > 0 and child.spelling not in visited_classes:
                new_class = DocClass(child)
                add_class(new_class.serialize(), offilename, new_class.folder)
                visited_classes.append(child.spelling)
                #clang_reference.add_class(new_class)

        elif clang_utils.is_function(child):
            if child.spelling not in visited_function and offilename != "ofMain":
                visited_function.append(child.spelling)
                new_func = DocFunction(child, None)
                add_function(new_func.serialize(), offilename, new_func.folder)
                #clang_reference.add_function(new_func)

        elif clang_utils.is_enum(child):
            if child.spelling not in visited_enums:
                new_enum = DocEnum(child)
                add_enum(new_enum.serialize(), offilename, new_enum.folder)
                visited_enums.append(child.spelling)

        elif clang_utils.is_typedef(child):
            if child.spelling not in visited_typedefs:
                add_typedef(DocTypedef(child).serialize(), offilename)
                visited_typedefs.append(child.spelling)
        #else:
        #   print "-- ",child.spelling, child.kind


def parse_folder(of_root, folder, files, is_addon=False):
    for name in files:
        filepath = os.path.join(folder, name)

        if name.split('.')[0] not in json_data.keys() and name.find('of') == 0 and os.path.splitext(name)[1] == '.h':
            tu = clang_utils.get_tu_from_file(filepath, of_root)
            for child in tu.cursor.get_children():
                parse_file_child(child)




def run(of_root, outdir):
    of_source = os.path.join(of_root, "libs/openFrameworks")

    # Prepare the outdir
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)

    # Run the clang parser
    for root, dirs, files in os.walk(of_source):
        parse_folder(of_root, root, files, False)


    """
    for addon in official_addons:
        for root, dirs, files in os.walk(os.path.join(of_addons, addon, "src")):
            dir_count += 1
            file_count += parse_folder(root, files, True)
    """

    # Save the output json data
    for key in json_data:
        json_file.save(outdir, key, json_data[key])

    # Save the reference file
    clang_reference.save(outdir)
