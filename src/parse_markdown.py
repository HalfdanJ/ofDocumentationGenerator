"""
Iterates over all json files, and adds markdown from manual written markdown files
"""
import os
import sys

import json
import json_file
import markdown_file

dir = os.path.dirname(__file__)

jsondir = os.path.join(dir,"../_json_documentation")

""" Get path of openframeworks from argv """
markdowndir = sys.argv[1]
print markdowndir

""" Check if the methods from markdown and js are matching"""
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

    for p1, p2 in zip(mdparams,jsparams):
        pp1 = p1.strip().split(' ')
        pp2 = p2.strip().split(' ')
        if pp1[0] != pp2[0]:
            return False

        if pp1[0] == 'const':
            if pp1[1] != pp2[1]:
                return False

    return True

""" Load the JSON file """
def loadJsonData(name):
    path = os.path.join(jsondir, name)

    if os.path.exists(path):
        with open(path) as data_file:
            return json.load(data_file)
    else:
        return None

def loadClassMarkdown(folder, name):
    return markdown_file.getclass(name, markdowndir)

def loadFunctionsMarkdown(folder, name):
    return markdown_file.getfunctionsfile(name, markdowndir)

""" Loads the markdown, and adds the description to JSON file"""
def enrichFile(data):
    markdownFunc = loadFunctionsMarkdown(data['folder'],data['name'])

    # Global functions
    for function in data['functions']:
        if 'description' in markdownFunc:
            function['markdown_description'] = markdownFunc['description']

        #methodfound = False
        for mdmethod in markdownFunc['functions']:
            if mdmethod['name'] == function['name'] and 'description' in mdmethod:
                if methodsMatching(mdmethod, function):
                    function['markdown_description'] = mdmethod['description']
                    #if methodfound:
                    #    raise Exception(function['name'],methodfound, parameters,function['parameters'] )
                    #methodfound = mdmethod['parameters']
                    ##break

    # Classes
    for classdata in data['classes']:
        markdownClass = loadClassMarkdown(data['folder'],classdata['name'])

        if 'description' in markdownClass:
            classdata['markdown_description'] = markdownClass['description']

        # Class methods
        for method in classdata['methods']:
            for mdmethod in markdownClass['functions']:
                if mdmethod['name'] == method['name'] and 'description' in mdmethod:
                    if methodsMatching(mdmethod, method):
                        method['markdown_description'] = mdmethod['description']
                        break

        # Class variables
        for variable in classdata['member_variables']:
            for mdvar in markdownClass['vars']:
                if mdvar['name'] == variable['name'] and 'description' in mdvar:
                    variable['markdown_description'] = mdvar['description']


""" RUN """

def run():
    for root, dirs, files in os.walk(jsondir):
        for name in files:
            if name[0] != '.' and name != 'reference.json':

                print name
                data = loadJsonData(name)

                enrichFile(data)
                json_file.save(jsondir, os.path.splitext(name)[0], data)


run()