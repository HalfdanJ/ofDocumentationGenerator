"""
Iterates over all json files, and adds markdown from manual written markdown files
"""
import os
import sys

import json

import re

import json_file
import markdown_file

LOOKUP_TABLE = {
    "<<":  "cpp_left_shift",
    ">>":  "cpp_right_shift",
    "&&":  "cpp_logical_and",
    "||":  "cpp_logical_or",
    "[]":  "cpp_subscript",
    "()":  "cpp_functional_form",
    "++":  "cpp_postfix_increment",
    "--":  "cpp_postfix_decrement",
    "->":  "cpp_member_access",
    "&":   "cpp_bitwise_and",
    "^":   "cpp_bitwise_xor",
    "|":   "cpp_bitwise_or",
    "=":   "cpp_assignment",
    "*=":  "cpp_multiplicative_assignment",
    "/=":  "cpp_division_assignment",
    "+=":  "cpp_additive_assignment",
    "-=":  "cpp_subtractive_assignment",
    "%=":  "cpp_modulo_assignment",
    ">>=": "cpp_right_shift_assignment",
    "<<=": "cpp_left_shift_assignment",
    "&=":  "cpp_bitwise_and_assignment",
    "^=":  "cpp_bitwise_xor_assignment",
    "|=":  "cpp_bitwise_or_assignment",
    "?:":  "cpp_conditional_assignment",
    "==":  "cpp_equality",
    "!=":  "cpp_not_equality",
    "*":   "cpp_multiplication",
    "+":   "cpp_addition",
    "-":   "cpp_subtraction",
    "/":   "cpp_division",
    "~":   "cpp_bitwise_not",
    "!":   "cpp_logical_not",
    ".":   "cpp_member_access",
    "%":   "cpp_modulo",
    ">":   "cpp_greater_than",
    "<":   "cpp_less_than",
    "<=":  "cpp_less_or_equal_than",
    ">=":  "cpp_greater_or_equal_than",
    ",":   "cpp_sequencing"
}

""" Check if the methods from markdown and js are matching"""

"""
def methodsMatching(mdfunction, jsfunction):
    mdreturns = mdfunction['returns']
    jsreturns = jsfunction['returns']

    if jsreturns != mdreturns:
        return False

    mdparams = mdfunction['parameters'].split(',')
    if len(mdparams) == 1 and mdparams[0] == '':
        mdparams = []

    jsparams = jsfunction['parameters']

    if len(mdparams) != len(jsparams):
        return False

    if len(mdparams) == len(jsparams) == 0:
        return True

    for p1, p2 in zip(mdparams, jsparams):
        pp1 = p1.strip().split(' ')
        pp2 = p2.strip().split(' ')

        for ii in range(0, len(pp1)):
            if pp1[ii] != pp2[ii]:
                return False

        if pp1[-1][0] == '*' or pp1[-1][0] == '&':
            if pp1[-1][0] != pp2[-1][0]:
                return False

    return True
"""

def getMarkdownMethodName(methodname):
    match = re.match("^operator(\\W+)", methodname, re.I | re.S)
    if match:
        operator = match.group(1)
        if LOOKUP_TABLE[operator]:
            return LOOKUP_TABLE[operator]
    return methodname

def cleanMarkup(mk, folder):
    rx = re.compile(r"!(\[.+\]\((.+)\))")
    for image in rx.finditer(mk):
        m = image.group(1)
        imgpath = image.group(2)
        imgpath = imgpath.replace('../', '')

        if len(imgpath.split('/')) == 1:
            imgpath = folder + '/' + imgpath

        m = m.replace(image.group(2), imgpath)
        mk = mk.replace(image.group(1), m)

    return mk


""" Load the JSON file """


def loadJsonData(name, jsondir):
    path = os.path.join(jsondir, name)

    if os.path.exists(path):
        with open(path) as data_file:
            return json.load(data_file)
    else:
        return None


def loadMarkdownFile(name, markdowndir):
    if not os.path.exists(os.path.join(markdowndir,name)):
        return None

    with open(os.path.join(markdowndir,name), 'r') as content_file:
        return content_file.read()

""" Loads the markdown, and adds the description to JSON file"""


def enrichFile(data, markdowndir):
    folder = data['folder']
    print data['name'], folder

    # Global functions
    for function in data['functions']:
        #print "- ",function['name']
        filename = data['folder']+'/'+data['name']+'.'+function['name']+'.md'
        #print "-- ",filename

        markdown = loadMarkdownFile(filename, markdowndir)
        if markdown:
            function['documentation']['markdown'] = cleanMarkup(markdown, folder)

    # Classes
    for classdata in data['classes']:
        filename = data['folder']+'/'+classdata['name']+'.md'
        print "- ",classdata['name']
        markdown = loadMarkdownFile(filename, markdowndir)
        if markdown:
            classdata['documentation']['markdown'] = cleanMarkup(markdown, folder)

        # Class methods
        for method in classdata['methods']:
            name = getMarkdownMethodName(method['name'])
            filename = data['folder']+'/'+classdata['name']+'.'+name+'.md'
            #print "- ",method['name'],name
            markdown = loadMarkdownFile(filename, markdowndir)
            if markdown:
                method['documentation']['markdown'] = cleanMarkup(markdown, folder)

        # Class variables
        for variable in classdata['member_variables']:
            filename = data['folder']+'/'+classdata['name']+'.'+variable['name']+'.md'
            print "- ",variable['name']
            markdown = loadMarkdownFile(filename, markdowndir)
            if markdown:
                variable['documentation']['markdown'] = cleanMarkup(markdown, folder)



    """
    markdownFunc = loadFunctionsMarkdown(data['folder'], data['name'], markdowndir)

    # Global functions
    for function in data['functions']:
        # methodfound = False
        for mdmethod in markdownFunc['functions']:
            if mdmethod['name'] == function['name'] and 'description' in mdmethod:
                if methodsMatching(mdmethod, function):
                    function['documentation']['markdown'] = cleanMarkup(mdmethod['description'], folder)
                    # if methodfound:
                    #    raise Exception(function['name'],methodfound, parameters,function['parameters'] )
                    # methodfound = mdmethod['parameters']
                    ##break

    # Classes
    for classdata in data['classes']:
        markdownClass = loadClassMarkdown(data['folder'], classdata['name'], markdowndir)

        if 'description' in markdownClass:
            classdata['documentation']['markdown'] = cleanMarkup(markdownClass['description'], folder)

        # Class methods
        for method in classdata['methods']:
            methodfound = False
            for mdmethod in markdownClass['functions']:
                if mdmethod['name'] == method['name'] and 'description' in mdmethod:
                    if methodsMatching(mdmethod, method):
                        method['documentation']['markdown'] = cleanMarkup(mdmethod['description'], folder)
                        # if methodfound:
                        #    raise Exception(mdmethod['name'],methodfound, mdmethod['parameters'],method['parameters'] )
                        # methodfound = mdmethod['parameters']
                        break

        # Class variables
        for variable in classdata['member_variables']:
            for mdvar in markdownClass['vars']:
                if mdvar['name'] == variable['name'] and 'description' in mdvar:
                    variable['documentation']['markdown'] = cleanMarkup(mdvar['description'], folder)
    """


""" RUN """


def run(markdowndir, jsondir):
    for root, dirs, files in os.walk(jsondir):
        for name in files:
            if name[0] != '.' and name != 'reference.json':
                #print name
                data = loadJsonData(name, jsondir)

                enrichFile(data, markdowndir)
                json_file.save(jsondir, os.path.splitext(name)[0], data)
                #print jsondir, os.path.splitext(name)[0]


if __name__ == '__main__':
    json_data_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_JSON_DIR', './_json_data'))
    markdown_root = os.path.abspath(os.getenv('OF_DOCUMENTATION_ROOT', ''))

    run(markdown_root, json_data_root)
