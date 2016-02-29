import json_file
import clang_utils

json_ref_data = []


def add_variable(var):
    json_ref_data.append({
        "file": clang_utils.filenameFromClangChild(var.cursor),
        "type": "variable",
        "name": var.data['name'],
        "folder": var.data['folder'],
        "class": var.parentclass.data['name']  if var.parentclass else None
    })

def add_function(func):
    json_ref_data.append({
        "file": clang_utils.filenameFromClangChild(func.cursor),
        "type": "function",
        "name": func.data['name'],
        "folder": func.data['folder'],
        "class": func.parentclass.data['name'] if func.parentclass else None
    })

def add_class(c):
    json_ref_data.append({
        "file": clang_utils.filenameFromClangChild(c.cursor),
        "type": "class",
        "folder": c.data['folder'],
        "name": c.data['name'],
    })

def add_enum(c):
    file = clang_utils.filenameFromClangChild(c.cursor)
    json_ref_data.append({
        "file": file,
        "type": "enum",
        "folder": c.data['folder'],
        "name": c.data['name'],
    })

    for o in c.data['options']:
        json_ref_data.append({
            "file": file,
            "type": "enum_option",
            "folder": c.data['folder'],
            "name": o['name'],
            "enum": c.data['name']
        })



def save(outdir):
    json_file.save(outdir,'reference',json_ref_data)
