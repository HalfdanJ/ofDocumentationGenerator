import json_file
import utils

json_ref_data = []


def add_variable(var):
    json_ref_data.append({
        "file": utils.filenameFromClangChild(var.cursor),
        "type": "variable",
        "name": var.data['name'],
        "class": var.parentclass.data['name']  if var.parentclass else None
    })

def add_function(func):
    json_ref_data.append({
        "file": utils.filenameFromClangChild(func.cursor),
        "type": "function",
        "name": func.data['name'],
        "class": func.parentclass.data['name'] if func.parentclass else None
    })

def add_class(c):
    json_ref_data.append({
        "file": utils.filenameFromClangChild(c.cursor),
        "type": "class",
        "name": c.data['name'],
    })


def save():
    json_file.save('reference',json_ref_data)
