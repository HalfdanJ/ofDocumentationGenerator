"""
This takes care of all the site generation using Jinja2
"""
import os

import shutil
import math
import re
from sets import Set

from scss import parser
from jinja2 import Environment, FileSystemLoader
import json
import time

from markdown_to_html import SiteParseMarkdown

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
loader = FileSystemLoader(template_dir)
env = Environment(loader=loader)

template = env.get_template('documentation_template.html')
toc_template = env.get_template('toc_template.html')

class SiteGenerator(object):
    """ Site generator """
    toc = {}
    jsondir = ''
    outdir = ''
    internal_files_rules = []
    file_filter = []

    markdownParser = SiteParseMarkdown()

    def getSourceUrl(self, filedata, item=None):
        ofUrl = 'https://github.com/openframeworks/openFrameworks'
        url = ofUrl+'/blob/master{}'
        url = url.format( filedata["file"])

        if item and 'line' in item and item['line']:
            url = url +'#L{}'.format(item['line'])
        return url

    def getMarkdownUrl(self, filedata, doc, item=None):
        name = item['name']
        if filedata['type'] == 'class':
            name = '{}.{}'.format(filedata['name'], item['name'])

        markdownUrl = 'https://github.com/workergnome/ofdocs_markdown/new/master/{}/?filename={}.md'
        markdownUrl = markdownUrl.format(filedata['folder'], name)

        if 'markdown' in doc and len(doc['markdown']) > 0:
            markdownUrl = 'https://github.com/workergnome/ofdocs_markdown/blob/master/{}/{}.md'
            markdownUrl = markdownUrl.format(filedata['folder'], name)

        return markdownUrl

    def currentTime(self):
        return time.strftime("%d %b %Y %H:%M UTC")

    """
    Parse an item (method, class variable etc), and return
    html version of the documenation ready to be rendered
    """
    def parseDocumentation(self, item, contextClass):
        doc = item['documentation']

        ret = {}
        ret["returns"] = self.markdownParser.parseMarkdown(doc["returns"], contextClass)
        ret["warning"] = self.markdownParser.parseMarkdown(doc["warning"], contextClass)
        ret["brief"] = self.markdownParser.parseMarkdown(doc['brief'], contextClass)


        if item['name'] == 'map':
            print 'MAP'
            print doc['brief']
            print doc["text"]

        #if doc['brief']:
        #    doc["text"] = doc["text"].replace(doc['brief'], '')
        ret["text"] = self.markdownParser.parseMarkdown(doc["text"], contextClass)

        if "markdown" in doc:
            ret["markdown"] = self.markdownParser.parseMarkdown(doc["markdown"], contextClass)

        if 'parameters' in item:
            ret["declaration"] = item['returns']+" "+item['name']+"("
            indent = ' '*len(ret['declaration'])
            #indent = ',\n'+indent

            params = []
            maxWidth = 0
            for p in item['parameter_names']:
                default = ' = '+item['parameter_defaults'][p] if p in item['parameter_defaults'] else ''
                txt = '{} {}{}'.format(item['parameter_types'][p], p, default)
                if maxWidth < len(txt):
                    maxWidth = len(txt)
                params.append(txt)

            i = 0
            for p in item['parameter_names']:
                if i != len(params)-1:
                    params[i] += ','
                else:
                    params[i] += ')'

                if p in doc['parameters']:
                    _indent = (1+maxWidth - len(params[i])) * ' '
                    params[i] += _indent+' // ' + doc['parameters'][p]

                params[i] += '\n'
                i+=1

            if len(params) == 0:
                ret["declaration"] += ')'
            else:
                 ret["declaration"] += indent.join(params)




        else:
            ret["declaration"] = '{type} {name};'.format(type=item['type'], name=item['name'])

        ret["declaration"] = self.markdownParser.parseMarkdown("```\n"+ret["declaration"]+"\n```", contextClass)

        ret["parameters"] = []

        if 'parameter_names' in item:
            for i in range(0, len(item['parameter_names'])):
                param_name = item['parameter_names'][i]

                param_doc = None
                if param_name in doc['parameters']:
                    param_doc = doc['parameters'][param_name]

                ret["parameters"].append({
                    'name': param_name,
                    'type': self.markdownParser.parseMarkdown(item['parameter_types'][param_name], contextClass),
                    'documentation': param_doc
                })

        # See also
        ret["sa"] = []
        for i in range(0, len(doc["sa"])):
            ret["sa"].append( self.markdownParser.parseMarkdown(doc["sa"][i], contextClass))

        return ret

    """
    Matches the internal_files file in markdown dir
    """
    def isFileInternal(self, file):
        import fnmatch
        return any(fnmatch.fnmatch(file, rule) for rule in self.internal_files_rules)

    """
    Creates a json file optimized for searching
    Different types are split up in different arrays, since types have
    different weight in search results
    """
    def generateSearchReference(self):
        data = {'files':[], 'classes':[], 'functions':[], 'variables':[], 'enums':[]}
        funcSet = Set()
        fileSet = Set()

        for item in self.reference:
            url = self.markdownParser.urlToReferenceItem(item),

            if not self.isFileInternal(item['file']):
                if item['file'] not in fileSet:
                    d = {
                        'name':item['file'],
                        'url':self.markdownParser.urlToFile(item['file'])
                    }
                    fileSet.add(item['file'])
                    data['files'].append(d)

                d = {
                    'name':item['name'],
                    'url':url
                }

                if item['type'] == 'class':
                    data['classes'].append(d)

                if item['type'] == 'function':
                    if item['name'] not in funcSet \
                        and item['name'][0] != '~'\
                        and item['name'] != item['class']:

                        d['class'] = item['class']
                        data['functions'].append(d)
                        funcSet.add(item['name'])

                if item['type'] == 'variable':
                    d['class'] = item['class']
                    data['variables'].append(d)

                if item['type'] == 'enum' or item['type'] == 'enum_option':
                    data['enums'].append(d)

                if item['type'] == 'typedef':
                    data['classes'].append(d)



        with open(os.path.join(self.outdir, "search.json"), 'w') as outfile:
            json.dump(data, outfile)


    def sectionAnchor(self, section, item):
        """
        :param section: section object
        :return: CamelCase version of the section name
        """
        if 'methods' in item:
            prefix = item['name']
        else:
            prefix = 'global'

        if section is None:
            return ""
        return prefix+'_'+''.join(x for x in section.title() if not x.isspace())

    def itemAnchor(self, item, parent):
        if  parent['type'] == 'class':
            prefix = parent['name']
        else:
            prefix = 'global'

        return prefix+'_'+item['name']

    """
    Parse item for all its functions, and return data ready to render by jinja
    """
    def parseItemFunctions(self, ret_methods, ret_sections, item, inherited):
        if 'methods' in item:
            methods = item['methods']
        else:
            methods = item['functions']

        for method in methods:
            if method['access'] != 'public' and method['access'] != 'invalid':
                continue
            if method['name'].startswith('~'):
                continue

            # Set section name if its not set already on the first element
            section = method["documentation"]["section"]

            # Set section name if its not set already on the first element
            if section is None and len(ret_methods) == 0 and item['type'] == 'class':
                section = method["documentation"]["section"] = 'Functions'

            if section and len(section) > 0 and (len(ret_sections) == 0 or ret_sections[-1] != section):
                ret_sections.append({
                    "title": section,
                    "anchor": self.sectionAnchor(section, item)
                })

            doc = self.parseDocumentation(method, item)

            new_variant = {
                "returns": method["returns"],
                "parameters": ', '.join(method["parameters"]),
                "parameter_types": ', '.join(method["parameter_types"]),
                "documentation": doc,
                "sourceUrl" : self.getSourceUrl(item, method),
                "markdownUrl": self.getMarkdownUrl(item, doc, method)
            }

            if inherited is not False:
                new_variant['inherited'] = inherited

            # Check if method is already added
            found = False
            for mm in ret_methods:
                if mm['name'] == method["name"]:

                    variant_found = False
                    for v in mm['variants']:
                        if v['parameter_types'] == new_variant['parameter_types']:
                            variant_found = True
                            # If the current added variant doesnt have a description, then take the description from
                            # the inherited member
                            if len(v["documentation"]['text']) == 0:
                                v["documentation"] = new_variant["documentation"]

                    if not variant_found:
                        mm['variants'].append(new_variant)

                    found = True
                    break

            # Method not alreay added, so add it
            if not found:
                ret_methods.append({
                    "name": method["name"],
                    "deprecated": method['deprecated'],
                    #"brief": self.parseBrief(method['documentation']),
                    "anchor": self.itemAnchor(method, item),
                    "section": section,
                    "section_anchor": self.sectionAnchor(section, item),
                    "variants": [new_variant]
                })

        # Add parent classes methods
        if 'extends' in item:
            for otherClassName in item['extends']:
                if len(otherClassName.strip()) > 0:
                    filename = otherClassName.strip()
                    filename = re.search("^([^<]*)", filename, re.I).group(0)

                    file = self.fileForClass(filename)
                    if file is not None:
                        data = self.loadData(file + ".json")
                        if data is not None:
                            for otherClass in data['classes']:
                                if otherClass['name'] == filename:
                                    self.parseItemFunctions(ret_methods, ret_sections, otherClass, filename)

    """
    Parse item for all its variables
    """
    def parseItemVariables(self, ret_variables, ret_sections, item):
        for variable in item["member_variables"]:
            if variable['access'] != 'public':
                continue

            section = variable["documentation"]["section"]
            # Set section name if its not set already on the first element
            if section is None and len(ret_variables) == 0:
                section = variable["documentation"]["section"] = 'Attributes'

            if section is not None and (len(ret_sections) == 0 or ret_sections[-1] != section):
                ret_sections.append({
                    "title": section,
                    "anchor": self.sectionAnchor(section, item)
                })

            ret_variables.append({
                "type": variable['type'],
                "name": variable["name"],
                "kind": variable['kind'],
                "anchor": self.itemAnchor(variable, item),
                "section": section,
                "section_anchor": self.sectionAnchor(section, item),
                "documentation": self.parseDocumentation(variable, item)
            })

    """
    Parse item for all its enums
    """
    def parseItemEnums(self, ret_enums, ret_sections, item):
        for enum in item["enums"]:
            section = enum["documentation"]["section"]
            # Set section name if its not set already on the first element
            if section is None and ( len(ret_enums) == 0 or ret_enums[-1]['type'] != enum['type']):
                section = enum["documentation"]["section"] = 'Enums'

            if section is not None and (len(ret_sections) == 0 or ret_sections[-1] != section):
                ret_sections.append({
                    "title": section,
                    "anchor": self.sectionAnchor(section, item)
                })

            ret_enums.append({
                "type": enum['type'],
                "name": enum["name"],
                "enum_options": enum['options'],
                "anchor": self.itemAnchor(enum, item),
                "section": section,
                "section_anchor": self.sectionAnchor(section, item),
                "documentation": self.parseDocumentation(enum, item)
            })

    def parseItemTypedefs(self, ret_typedefs, ret_sections, item):
        for typedef in item['typedefs']:
            section = typedef["documentation"]["section"]
            # Set section name if its not set already on the first element
            if section is None and ( len(ret_typedefs) == 0 or ret_typedefs[-1]['type'] != typedef['type']):
                section = typedef["documentation"]["section"] = 'Typedefs'

            if section is not None and (len(ret_sections) == 0 or ret_sections[-1] != section):
                ret_sections.append({
                    "title": section,
                    "anchor": self.sectionAnchor(section, item)
                })

            ret_typedefs.append({
                "type": typedef['type'],
                "name": typedef["name"],
                "typedef_type": typedef['typedef_type'],
                "anchor": self.itemAnchor(typedef, item),
                "section": section,
                "section_anchor": self.sectionAnchor(section, item),
                "documentation": self.parseDocumentation(typedef, item)
            })

    """
    Render TOC (frontpage)
    """
    def renderToc(self, toc):
        extra = 1

        # remove internal files from toc
        for key in toc.keys():
            #toc[key] = filter(lambda file: not self.isFileInternal(file), toc[key])
            for file in toc[key]:
                file['internal'] = self.isFileInternal(file['file'])
            toc[key].sort()

        core = []
        addons = []
        for key in sorted(toc.keys()):
            if len(toc[key]) > 0:
                if key.startswith('ofx'):
                    addons.append({ 'name': key, 'files': toc[key] })
                else:
                    core.append({ 'name': key.upper(), 'files': toc[key] })


        output = toc_template.render({
            "core": core,
            "addons": addons,
            "date": self.currentTime()
        }).encode('utf8')

        # to save the results
        with open(os.path.join(self.outdir, "index.html"), "wb") as fh:
            fh.write(output)

    """
    Render documentation item
    """
    def renderFile(self, filedata):
        render_data = {
            "file": filedata["name"],
            "folder": filedata['folder'],
            "content": [],
            "otherFilesInFolder" : [],
            "date": self.currentTime()
        }

        # Find other files in same folder
        for r in self.reference:
            if r['folder'] == filedata['folder'] and r['file'] not in render_data['otherFilesInFolder']:
                render_data['otherFilesInFolder'].append(r['file'])

        # Init values
        global_sections = []
        global_methods = []
        global_attributes = []

        # Global functions
        self.parseItemFunctions(global_methods, global_sections, filedata, False)
        # Global enums
        self.parseItemEnums(global_attributes, global_sections, filedata)
        # Global typedefs
        self.parseItemTypedefs(global_attributes, global_sections, filedata)

        # If there is anything global
        if len(global_methods) > 0 or len(global_attributes) > 0:
            render_data['content'].append({
                "documentation": None, # TODO
                #"name": "Global functions",
                "name": filedata['name'],
                "methods": global_methods,
                "member_variables": global_attributes,
                "sections": global_sections,
                "extends": None,
                "type": 'global',
                "sourceUrl" : self.getSourceUrl(filedata),

            })


        # Classes
        for subitem in filedata['classes']:
            if not subitem['visible']:
                continue
            sections = []

            # Member methods
            methods = []
            self.parseItemFunctions(methods, sections, subitem, False)

            # Member variables
            member_variables = []
            self.parseItemVariables(member_variables, sections, subitem)

            # Extends
            extends =  map(lambda name:
                self.markdownParser.linkToReferenceItem(self.markdownParser.searchForGlobalReference(name,''),name), subitem['extends'])

            doc = self.parseDocumentation(subitem, subitem)


            # Class item
            render_data['content'].append({
                "documentation": doc,
                "name": subitem['name'],
                "methods": methods,
                "member_variables": member_variables,
                "sections": sections,
                "extends": extends,
                "type": 'class',
                "sourceUrl" : self.getSourceUrl(filedata, subitem),
                "markdownUrl": self.getMarkdownUrl(filedata, doc, subitem)
            })


        if len(render_data['content']) == 1 and render_data['content'][0]['name'] == render_data['file']:
            render_data['showPageTitle'] = False
        else:
            render_data['showPageTitle'] = True

        # save the results
        output = template.render(render_data).encode('utf8')
        outpath = os.path.join(self.outdir, filedata['name'] + ".html")
        with open(outpath, "wb") as fh:
            fh.write(output)

        os.chmod(outpath, 0o777)

    def fileForClass(self, name):
        for r in self.reference:
            if r['type'] == 'class' and r['name'] == name:
                return r['file']

    def loadData(self, name):
        path = os.path.join(self.jsondir, name)

        if os.path.exists(path):
            with open(path) as data_file:
                return json.load(data_file)
        else:
            return None

    def updateToc(self, filedata):
        if filedata['folder'] not in self.toc:
            self.toc[filedata['folder']] = []

        self.toc[filedata['folder']].append({'file':filedata['name']})


    def compileScss(self):
        with open(os.path.join(self.outdir ,"style.css"), "w") as output:
            scssPath = os.path.join(template_dir,'style.scss')
            #print scssPath
            parsedScss = parser.load(scssPath)
            output.write(parsedScss)


    ''' RUN '''
    def run(self, markdowndir, jsondir, outdir):
        self.jsondir = jsondir
        self.outdir = outdir

        self.reference = self.loadData('reference.json')

        with open(os.path.join(markdowndir, 'internal_files'),'r') as internal_files:
            self.internal_files_rules = internal_files.read().split('\n')

        self.markdownParser.outdir = self.outdir
        self.markdownParser.markdowndir = markdowndir
        self.markdownParser.reference = self.reference
        self.markdownParser.populateLookupTable()

        print "Site Generator - cleanup"
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        os.makedirs(outdir)

        print "Site Generator - start individual pages"
        for root, dirs, files in os.walk(jsondir):
            for name in files:
                if name[0] != '.' and name != 'reference.json':
                    data = self.loadData(name)
                    #if name == 'ofRectangle.json':
                    if len(self.file_filter) == 0 or name.replace('.json', '') in self.file_filter:
                        print "Site Generator - Parse "+name
                        self.renderFile(data)
                    self.updateToc(data)

        print "Site Generator - Generate index"
        self.renderToc(self.toc)
        self.generateSearchReference()

        self.compileScss()
