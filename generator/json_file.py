import os
import json

documentation_root = '../_json_documentation/'


def save(name, data, is_addon=False):
    path = ""
    if is_addon:
        path = os.path.join(documentation_root,"addons")
    else:
        path = os.path.join(documentation_root)

    try:
        os.mkdir(path)
    except:
        pass



    with open(os.path.join(path,name)+".json", 'w') as outfile:
        json.dump(data, outfile, indent=4,)
