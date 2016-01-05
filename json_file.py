from documentation_members import DocsMethod
from documentation_members import DocsVar
from documentation_class import DocsClass
from documentation_function import DocsFunctionsFile, DocsFunction
import os
import json

documentation_root = '_json_documentation/'


def save_class(clazz,is_addon=False):
    path = ""
    if is_addon:
        path = os.path.join(documentation_root,"addons",clazz.module)
    else:
        path = os.path.join(documentation_root,clazz.module)

    try:
        os.mkdir(path)
    except:
        pass



    with open(os.path.join(path,clazz.name)+".json", 'w') as outfile:
        json.dump(clazz.serialize(), outfile, indent=4,)