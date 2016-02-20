import os

import markdown as markdown
import shutil
import sys

import re

from scss import parser
from jinja2 import Environment, FileSystemLoader
import json

dir = os.path.dirname(__file__)

markdowndir = sys.argv[1]

outdir = os.path.join(dir,'../_site/latest/')
template_dir = os.path.join(dir,'templates')


def parseMarkdown(mk):
    if mk is None:
        return ""
    ret = markdown.markdown(mk, extensions=['codehilite', 'fenced_code'])
    ret = ret.replace("<code", "<code class='prettyprint lang-cpp'")

    rx = re.compile(r"!\[.+\]\((.+)\)")
    for image in rx.finditer(mk):
        imgpath = image.group(1)
        imgpath = imgpath.replace('../','')
        dest = os.path.join(outdir, imgpath)

        imgpath = os.path.join(markdowndir, imgpath)

        if not os.path.exists(os.path.dirname(os.path.abspath(dest))):
            os.makedirs(os.path.dirname(os.path.abspath(dest)))

        if os.path.exists(imgpath) and not os.path.exists(dest):
            print "copy image  ",imgpath
            shutil.copyfile(imgpath, dest)
        #else:
        #    raise Exception('Image '+imgpath+" doesnt exist!")
    return ret


def parseDocumentation(doc):
    doc["returns"] = parseMarkdown(doc["returns"])
    doc["warning"] = parseMarkdown(doc["warning"])
    doc["text"] = parseMarkdown(doc["text"])

    if "markdown" in doc:
        doc["markdown"] = parseMarkdown(doc["markdown"])

    for key in doc["parameters"].iterkeys():
        doc["parameters"][key] = parseMarkdown(doc["parameters"][key])

    for i in range(0, len(doc["sa"])):
        doc["sa"][i] = parseMarkdown(doc["sa"][i])

    return doc


def renderToc(toc):
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


def sectionAnchor(section, item):
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


def parseItemFunctions(methods, sections, item, inherited):

    if 'methods' in item:
        functions = item['methods']
    else:
        functions = item['functions']

    for method in functions:
        if method['access'] != 'public' and method['access'] != 'invalid':
            continue
        if method['name'].startswith('~'):
            continue
        if method['deprecated'] is True:
            continue


        # try:
        # Set section name if its not set already on the first element
        section = method["documentation"]["section"]
        if section and len(section) == 0 and len(methods) == 0:
            section = method["documentation"]["section"] = 'Functions'

        if section and len(section) > 0 and (len(sections) == 0 or sections[-1] != section):
            sections.append({
                "title": section,
                "anchor": sectionAnchor(section,item)
            })

        m = {
            "returns": method["returns"],
            "parameters": ', '.join(method["parameters"]),
            "documentation": parseDocumentation(method["documentation"])
        }

        if inherited is not False:
            m['inherited'] = inherited

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
                "section_anchor": sectionAnchor(section,item),
                "variants": [m]
            })

            # except:
            #    pass
    if 'extends' in item:
        for otherClassName in item['extends']:
            if len(otherClassName.strip()) > 0:
                filename = otherClassName.strip()
                filename = re.search("^([^<]*)", filename, re.I).group(0)

                file = fileForClass(filename)
                if file is not None:
                    data = loadData(file + ".json")
                    if data is not None:
                        for otherClass in data['classes']:
                            if otherClass['name'] == filename:
                                parseItemFunctions(methods, sections, otherClass, filename)




def renderFile(filedata):
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)

    template = env.get_template('documentation_template.html')
    render_data = {
        "pageTitle": filedata["name"],
        "content": []
    }

    sections = []
    methods = []

    parseItemFunctions(methods, sections, filedata, False)
    render_data['content'].append({
        "documentation": None,
        "name": "Functions",
        "methods": methods,
        "member_variables": [],
        "sections": sections,
        "extends": None
    })

    for subitem in filedata['classes']:
        if not subitem['visible']:
            continue
        sections = []
        methods = []

        parseItemFunctions(methods, sections, subitem, False)

        member_variables = []
        for variable in subitem["member_variables"]:
            if variable['access'] != 'public':
                continue

            section = variable["documentation"]["section"]
            # Set section name if its not set already on the first element
            if section is None and len(member_variables) == 0:
                section = variable["documentation"]["section"] = 'Attributes'

            if section is not None and (len(sections) == 0 or sections[-1] != section):
                sections.append({
                    "title": section,
                    "anchor": sectionAnchor(section, subitem)
                })

            member_variables.append({
                "type": variable['type'],
                "name": variable["name"],
                "section": section,
                "section_anchor": sectionAnchor(section, subitem),
                "documentation": parseDocumentation(variable["documentation"])
            })


        render_data['content'].append({
            "documentation": parseDocumentation(subitem["documentation"]),
            "name": subitem['name'],
            "methods": methods,
            "member_variables": member_variables,
            "sections": sections,
            "extends": subitem['extends']
        })

    # save the results
    output = template.render(render_data).encode('utf8')
    outpath = outdir + filedata['name'] + ".html"
    with open(outpath, "wb") as fh:
        fh.write(output)

    os.chmod(outpath, 0o777)

def fileForClass(name):
    for r in reference:
        if r['type'] == 'class' and r['name'] == name:
            return r['file']

    print name +" NOT FOUND"

def loadData(name):
    path = os.path.join(dir,'../_json_documentation', name)

    if os.path.exists(path):
        with open(path) as data_file:
            return json.load(data_file)
    else:
        return None


toc = {}


def updateToc(filedata):
    if filedata['folder'] not in toc:
        toc[filedata['folder']] = []

    toc[filedata['folder']].append(filedata['name'])


def compileScss():
    with open(outdir + "style.css", "w") as output:
        scssPath = os.path.join(template_dir,'style.scss')
        print scssPath
        parsedScss = parser.load(scssPath)
        output.write(parsedScss)


''' RUN '''

if os.path.exists(outdir):
    shutil.rmtree(outdir)
os.makedirs(outdir)

reference = loadData('reference.json')

for root, dirs, files in os.walk(os.path.join(dir,"../_json_documentation")):
    for name in files:
        if name[0] != '.' and name != 'reference.json':
            print name

            data = loadData(name)
            renderFile(data)
            updateToc(data)


renderToc(toc)
compileScss()
shutil.copyfile(os.path.join(template_dir,'script.js'), os.path.join(outdir,'script.js'))

print "Done generating site"
