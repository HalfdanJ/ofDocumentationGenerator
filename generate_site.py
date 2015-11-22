import markdown as markdown
from scss import parser
from jinja2 import Environment, FileSystemLoader
import json

def ParseMarkdown(mk):
    ret = markdown.markdown( mk, extensions=[ 'codehilite', 'fenced_code'])
    ret = ret.replace("<code", "<code class='prettyprint'")
    return ret

def RenderFile(clazz):
    print clazz
    template_dir = 'templates'
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)

    template = env.get_template('documentation_template.html')

    methods = []

    for method in clazz["methods"]:
        methods.append({
            "name": method["name"],
            "returns": method["returns"],
            "parameters": method["parameters"],

            "inlined_description": ParseMarkdown(method["inlined_description"])
        })

    output = template.render({
        "pageTitle": clazz["className"],
        "inline_description": ParseMarkdown(clazz["inline_description"]),
        "description": ParseMarkdown(clazz["description"]),

        "methods": methods
    }).encode('utf8')


    # to save the results
    with open("_site/"+clazz["className"]+".html", "wb") as fh:
        fh.write(output)


def CompileScss():
    with open("_site/style.css", "w") as output:
        output.write(parser.load('templates/style.scss'))

with open('_documentation/ofCamera.json') as data_file:
    data = json.load(data_file)
    RenderFile(data)


CompileScss()
