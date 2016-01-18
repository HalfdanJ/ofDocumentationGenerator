import os

import markdown as markdown
import shutil

import re
from scss import parser
from jinja2 import Environment, FileSystemLoader
import json

outdir = '_site/'


def parseMarkdown(mk):
    if mk is None:
        return ""
    ret = markdown.markdown(mk, extensions=['codehilite', 'fenced_code'])
    ret = ret.replace("<code", "<code class='prettyprint lang-cpp'")
    return ret


def parseDocumentation(doc):
    doc["returns"] = parseMarkdown(doc["returns"])
    doc["warning"] = parseMarkdown(doc["warning"])
    doc["text"] = parseMarkdown(doc["text"])

    for key in doc["parameters"].iterkeys():
        doc["parameters"][key] = parseMarkdown(doc["parameters"][key])

    for i in range(0,len(doc["sa"])):
        doc["sa"][i] = parseMarkdown(doc["sa"][i])

    return doc


def renderToc(toc):
    template_dir = 'templates'
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)

    template = env.get_template('toc_template.html')

    output = template.render({
        "folders": toc.keys(),
        "content": toc
    }).encode('utf8')

    # to save the results
    with open(outdir + "index.html", "wb") as fh:
        fh.write(output)


def sectionAnchor(section):
    """
    :param section: section object
    :return: CamelCase version of the section name
    """
    if section is None:
        return ""
    return ''.join(x for x in section.title() if not x.isspace())


def parseMethods(methods, sections, clazz, inherited):
    for method in clazz["methods"]:
        if method['access'] != 'public':
            continue
        if method['name'].startswith('~'):
            continue


        #try:
            # Set section name if its not set already on the first element
        section = method["documentation"]["section"]
        if section and len(section) == 0 and len(methods) == 0:
            section = method["documentation"]["section"] = 'Functions'

        if section and len(section) > 0 and (len(sections) == 0 or sections[-1] != section):
            sections.append({
                "title": section,
                "anchor": sectionAnchor(section)
            })

        m = {
            "returns": method["returns"],
            "parameters": method["parameters"],
            "documentation": parseDocumentation(method["documentation"])
        }

        if inherited:
            m['inherited'] = clazz["className"]

        # Check if method is already added
        found = False
        for mm in methods:
            if mm['name'] == method["name"]:

                variant_found = False
                for v in mm['variants']:
                    if v['parameters'] == m['parameters']:
                        variant_found = True
                        # If the current added variant doesnt have a description, then take the description from
                        # the inherited member
                        if len(v["documentation"]['text']) == 0:
                            v["documentation"]['text'] = m["documentation"]['text']

                if not variant_found:
                    mm['variants'].append(m)

                found = True
                break

        if not found:
            methods.append({
                "name": method["name"],
                "section": section,
                "section_anchor": sectionAnchor(section),
                "variants": [m]
            })

        #except:
        #    pass

    for otherClassName in clazz['extends']:
        if len(otherClassName.strip()) > 0:
            filename = otherClassName.strip()
            filename = re.search("^([^<]*)", filename, re.I).group(0)

            data = loadDataForClass(filename + ".json")
            if data is not None:
                parseMethods(methods, sections, data, True)


def renderFile(clazz):
    template_dir = 'templates'
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)

    template = env.get_template('documentation_template.html')

    sections = []
    methods = []

    parseMethods(methods, sections, clazz, False)

    member_variables = []
    for variable in clazz["member_variables"]:
        if variable['access'] != 'public':
            continue

        try:
            section = variable["documentation"]["section"]
            # Set section name if its not set already on the first element
            if len(section) == 0 and len(member_variables) == 0:
                section = variable["documentation"]["section"] = 'Attributes'

            if len(section) > 0 and (len(sections) == 0 or sections[-1] != section):
                sections.append({
                    "title": section,
                    "anchor": sectionAnchor(section)
                })

            member_variables.append({
                "type": variable['type'],
                "name": variable["name"],
                "section": section,
                "section_anchor": sectionAnchor(section),
                "documentation": parseDocumentation(variable["documentation"])
            })

        except:
            pass

    output = template.render({
        "pageTitle": clazz["className"],
        "inline_description": parseMarkdown(clazz["inline_description"]),
        "description": parseMarkdown(clazz["description"]),

        "methods": methods,
        "member_variables": member_variables,
        "sections": sections,
        "extends": clazz['extends']
    }).encode('utf8')

    # to save the results
    with open(outdir + clazz["className"] + ".html", "wb") as fh:
        fh.write(output)


def loadDataForClass(className):
    path = os.path.join('_json_documentation', className)

    if os.path.exists(path):
        with open(path) as data_file:
            return json.load(data_file)
    else:
        return None


toc = {}


def updateToc(clazz):
    if clazz['path'] not in toc:
        toc[clazz['path']] = []

    toc[clazz['path']].append(clazz['className'])


def compileScss():
    with open(outdir + "style.css", "w") as output:
        output.write(parser.load('templates/style.scss'))


''' RUN '''

if not os.path.exists(outdir):
    os.makedirs(outdir)

for root, dirs, files in os.walk("_json_documentation"):
    for name in files:
        if name[0] != '.':
            data = loadDataForClass(name)
            renderFile(data)
            updateToc(data)
            print name

renderToc(toc)
compileScss()
shutil.copyfile('templates/script.js', '_site/script.js')
