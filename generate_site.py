import os

import markdown as markdown
import shutil
from scss import parser
from jinja2 import Environment, FileSystemLoader
import json

outdir = '_site/'

def ParseMarkdown(mk):
    ret = markdown.markdown( mk, extensions=[ 'codehilite', 'fenced_code'])
    ret = ret.replace("<code", "<code class='prettyprint'")
    return ret

def renderToc(toc):
    template_dir = 'templates'
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)

    template = env.get_template('toc_template.html')

    methods = []


    output = template.render({
        "folders": toc.keys(),
        "content":toc
    }).encode('utf8')


    # to save the results
    with open(outdir+"index.html", "wb") as fh:
        fh.write(output)

def sectionAnchor(section):
    return  ''.join(x for x in section.title() if not x.isspace())

def renderFile(clazz):
    #print clazz
    template_dir = 'templates'
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)

    template = env.get_template('documentation_template.html')

    sections = []
    methods = []
    for method in clazz["methods"]:
        try:
            if method["section"] is not None and ( len(sections) == 0 or sections[-1] != method["section"]):
                sections.append({
                    "title": method["section"],
                    "anchor": sectionAnchor(method["section"])
                })

            m = {
                    "returns": method["returns"],
                    "parameters": method["parameters"],
                    "inlined_description": ParseMarkdown(method["inlined_description"])
                }

            if len(methods) == 0 or methods[-1]['name'] != method['name']:
                methods.append({
                    "name": method["name"],
                    "section": method["section"],
                    "section_anchor": sectionAnchor(method["section"]),
                    "variants": [m]
                })
            else:
                methods[-1]['variants'].append(m)

        except:
            pass

    member_variables = []
    for variable in clazz["member_variables"]:
        try:
            if variable["section"] is not None and ( len(sections) == 0 or sections[-1] != variable["section"]):
                sections.append({
                    "title": variable["section"],
                    "anchor": sectionAnchor(variable["section"])
                })

            m = {
                    "inlined_description": ParseMarkdown(variable["inlined_description"])
                }

            if len(member_variables) == 0 or member_variables[-1]['name'] != variable['name']:
                member_variables.append({
                    "type" : variable['type'],
                    "name": variable["name"],
                    "section": variable["section"],
                    "section_anchor": sectionAnchor(variable["section"]),
                    "variants": [m]
                })
            else:
                member_variables[-1]['variants'].append(m)

        except:
            pass

    print member_variables
    output = template.render({
        "pageTitle": clazz["className"],
        "inline_description": ParseMarkdown(clazz["inline_description"]),
        "description": ParseMarkdown(clazz["description"]),

        "methods": methods,
        "member_variables": member_variables,
        "sections": sections
    }).encode('utf8')

    print sections
    # to save the results
    with open(outdir+clazz["className"]+".html", "wb") as fh:
        fh.write(output)


toc = {}
def updateToc(clazz):
    if clazz['path'] not in toc:
        toc[clazz['path']] = []

    toc[clazz['path']].append(clazz['className'])


def compileScss():
    with open(outdir+"style.css", "w") as output:
        output.write(parser.load('templates/style.scss'))


''' RUN '''

if not os.path.exists(outdir):
    os.makedirs(outdir)


for root, dirs, files in os.walk("_json_documentation"):
    for name in files:
        with open(os.path.join('_json_documentation',name)) as data_file:
            data = json.load(data_file)
            renderFile(data)
            updateToc(data)
            print name



renderToc(toc)
compileScss()
shutil.copyfile('templates/script.js', '_site/script.js');