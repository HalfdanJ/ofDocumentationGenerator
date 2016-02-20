"""
Iterates over all json files, and adds markdown from manual written markdown files
"""
import os
import sys

import json

import re

import json_file
import markdown_file

dir = os.path.dirname(__file__)

jsondir = os.path.join(dir,"../_json_documentation")

""" Get path of openframeworks from argv """
markdowndir = sys.argv[1]

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

        i = len(pp1)-1

        """
        if pp1[i] == 'const':
            i += 1

        if pp1[i][-1] == '<':
            i += 1
        """
        for ii in range(0, i+1):
            if pp1[ii] != pp2[ii]:
                return False

        if pp1[-1][0] == '*' or pp1[-1][0] == '&':
            if pp1[-1][0] != pp2[-1][0]:
                return False

    return True

def cleanMarkup(mk, folder):
    rx = re.compile(r"!(\[.+\]\((.+)\))")
    for image in rx.finditer(mk):
        m = image.group(1)
        imgpath = image.group(2)
        imgpath = imgpath.replace('../','')

        if len(imgpath.split('/')) == 1:
            print imgpath
            imgpath = folder + '/' + imgpath
            m = m.replace(image.group(2), imgpath)
            mk = mk.replace(image.group(1), m)
            print imgpath
    return mk



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
    folder = data['folder']

    # Global functions
    for function in data['functions']:
        #methodfound = False
        for mdmethod in markdownFunc['functions']:
            if mdmethod['name'] == function['name'] and 'description' in mdmethod:
                if methodsMatching(mdmethod, function):
                    function['documentation']['markdown'] = cleanMarkup(mdmethod['description'], folder)
                    #if methodfound:
                    #    raise Exception(function['name'],methodfound, parameters,function['parameters'] )
                    #methodfound = mdmethod['parameters']
                    ##break

    # Classes
    for classdata in data['classes']:
        markdownClass = loadClassMarkdown(data['folder'],classdata['name'])

        if 'description' in markdownClass:
            classdata['documentation']['markdown'] = cleanMarkup(markdownClass['description'], folder)

        # Class methods
        for method in classdata['methods']:
            methodfound = False
            for mdmethod in markdownClass['functions']:
                if mdmethod['name'] == method['name'] and 'description' in mdmethod:
                    if methodsMatching(mdmethod, method):
                        method['documentation']['markdown'] = cleanMarkup(mdmethod['description'],folder)
                        #if methodfound:
                        #    raise Exception(mdmethod['name'],methodfound, mdmethod['parameters'],method['parameters'] )
                        #methodfound = mdmethod['parameters']
                        break

        # Class variables
        for variable in classdata['member_variables']:
            for mdvar in markdownClass['vars']:
                if mdvar['name'] == variable['name'] and 'description' in mdvar:
                    variable['documentation']['markdown'] = cleanMarkup(mdvar['description'], folder)


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