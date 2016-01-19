#!/usr/bin/python
import os
import re
import HTMLParser
import sys

import json_file
from documentation_members import DocsVar
from documentation_class import DocClass
import documentation_parser
import clang_utils
import utils
from clang.cindex import CursorKind, TokenKind

of_root = sys.argv[1]
of_source = os.path.join(of_root, "libs/openFrameworks")

of_addons = os.path.join(of_root, "addons")
official_addons = [
                    "ofxAccelerometer",
                    "ofxAndroid",
                    "ofxAssimpModelLoader",
                    "ofxEmscripten",
                    "ofxGui",
                    "ofxNetwork",
                    "ofxOpenCv",
                    "ofxOsc",
                    "ofxSvg",
                    "ofxThreadedImageLoader",
                    "ofxXmlSettings",                    
                  ]
currentversion = "0.9.0"
alternatives = { 
                 'size_t': ['int', 'unsigned int', 'long', 'unsigned long'],
                 'filesystem::path': ['string'],
                 'ofIndexType': ['int', 'unsigned int', 'long'],
                 'unsigned long': ['int', 'unsigned int', 'long'],
                 'unsigned long long': ['int', 'unsigned int', 'long'],
               }

def substitutetype(ty):
    """ fix types to match the standard format in the final docs,
        removes std:: and adds a leading and trailing space between
        triangular brackets """
        
    ty = ty.replace("std::", "")
    ty = re.sub(r"(.*)<(.*)>","\\1< \\2 >",ty)
    return ty


def parse_variable(documentation_class, clazz, member):
    var = documentation_class.var_by_name(member.displayname)
    if not var:
        var = DocsVar(0)
        var.name = member.spelling
        var.access = member.access_specifier.name.lower()
        var.version_started = currentversion
        var.version_deprecated = ""
        var.constant = member.result_type.is_volatile_qualified()
        var.static = member.kind == CursorKind.VAR_DECL
        var.clazz = documentation_class.name
        var.type = substitutetype(member.type.spelling)
        new_vars.append(var)
    try:
        var.documentation = documentation_parser.parse_docs(member)

        if var.documentation['internal']:
            var.visible = False

    except:
        pass

    json_ref_data.append({
        "file": utils.filenameFromClangChild(member),
        "type": "variable",
        "name": var.name,
        "class": documentation_class.name
    })

    return var
    
    
def parse_function(documentation_class, clazz, member, already_found, fuzzy=False):
    """ Parse a clang function and return a DocsMethod"""
    params = ""

    # Parse the arguments into a stirng
    for arg in member.get_children():
        if arg.kind.is_attribute():
            # TODO: we suppose only attributes are the deprecated ones 
            return None
        if arg.kind != CursorKind.PARM_DECL:
            continue
        if len(params) > 0:
            params += ", "
        argtype = substitutetype(arg.type.spelling)
        if argtype[-1]=='&' or argtype[-1]=='*':
            params += argtype + arg.spelling
        else:
            params += argtype + " " + arg.spelling
        
        for part in arg.get_children():
            if part.kind == CursorKind.INTEGER_LITERAL or \
               part.kind == CursorKind.CHARACTER_LITERAL or \
               part.kind == CursorKind.CXX_BOOL_LITERAL_EXPR or \
               part.kind == CursorKind.CXX_NULL_PTR_LITERAL_EXPR or \
               part.kind == CursorKind.FLOATING_LITERAL or \
               part.kind == CursorKind.IMAGINARY_LITERAL or \
               part.kind == CursorKind.OBJC_STRING_LITERAL or \
               part.kind == CursorKind.OBJ_BOOL_LITERAL_EXPR or \
               part.kind == CursorKind.STRING_LITERAL:
                try:
                    params += "=" + part.get_tokens().next().spelling
                except:
                    print "error trying to print default value for " + documentation_class.name + "::" + member.spelling + " " + arg.spelling + " = " + str(part.kind)
                    pass
            elif part.kind == CursorKind.DECL_REF_EXPR:    
                params += "=" + part.spelling

    # Method name
    methodname = member.spelling
    methodname = re.sub("<.*>","",methodname)

    # Returns
    if member.kind == CursorKind.CONSTRUCTOR or member.kind == CursorKind.DESTRUCTOR or (not clazz is None and methodname == clazz.spelling):
        returns = ""
    else:
        returns = substitutetype(member.result_type.spelling)
        returns = ("" if returns is None else returns)

    method = documentation_class.function_by_signature(methodname, returns, params, alternatives, already_found, fuzzy)
    
    if method is None:
        return None
    
    if not clazz is None:
        method.static = member.is_static_method()
        method.clazz = documentation_class.name
        method.access = member.access_specifier.name.lower()
    else:
        method.functionsfile = documentation_class.name

    method.returns = returns

    #method.description = method.description.replace('<p>','').replace('</p>','').replace('<code>','').replace('</code>','').replace('<pre>','')
    
    if method.new:
        method.version_started = currentversion

    method.documentation = documentation_parser.parse_docs(member)
    if method.documentation['internal']:
        method.visible = False

    if method.new:
        if clazz is None:
            new_functions.append(method)
        else:
            new_methods.append(method)

    json_ref_data.append({
        "file": utils.filenameFromClangChild(member),
        "type": "function",
        "name": methodname,
        "class": documentation_class.name
    })
    return method
    
            
def serialize_functionfile(cursor,filename,is_addon=False):
    functionsfile = markdown_file.getfunctionsfile(filename)
    functions_fromcode = []
    functions_for_fuzzy_search = []
    for member in cursor.get_children():
        if is_function(member) and str(member.location.file) == cursor.spelling: 
            function = parse_function(functionsfile, None, member, functions_fromcode)
            if function is not None:
                functions_fromcode.append(function)
            else:
                functions_for_fuzzy_search.append(member)
    
    for member in functions_for_fuzzy_search:
        function = parse_function(functionsfile, None, member, functions_fromcode, True)
        if function is not None:
            functions_fromcode.append(function)
                
    thisfile_missing_functions = []
    for function in functionsfile.function_list:
        if not function in functions_fromcode:
            missing_functions.append(function)
            thisfile_missing_functions.append(function)
    
    for function in thisfile_missing_functions:
        functionsfile.function_list.remove(function)
                
    #functionsfile.function_list.sort(key=lambda function: function.name)
    #if len(functionsfile.function_list)>0:
    #    markdown_file.setfunctionsfile(functionsfile,is_addon)

def serialize_function(cursor, filename, is_addon=False):
    if utils.is_function(cursor):
        return parse_function()
def serialize_class(cursor,is_addon=False, parent=None):

    clazz = cursor
    classname = (parent + "::" if parent is not None else "") + clazz.spelling
    print "Serialize class "+classname

    documentation_class = markdown_file.getclass(classname)

    documentation_class.path = os.path.dirname(clazz.location.file.name).replace(os.path.join(of_root,"libs/openFrameworks/"),"")

    current_variables_list = []
    current_methods_list = []
    methods_for_fuzzy_search = []

    documentation_class.extends = []
    
    for child in clazz.get_children():
        if child.kind == CursorKind.CXX_BASE_SPECIFIER:
            if child.spelling.find("class") == 0:
                baseclass = child.spelling.split(' ')[1]
                documentation_class.extends.append(baseclass)
            else:
                documentation_class.extends.append(child.spelling)

    documentation_class.documentation = documentation_parser.parse_docs(clazz)

    if documentation_class.documentation['internal']:
        documentation_class.visible = False

    for member in clazz.get_children():
        if member.kind == CursorKind.CLASS_DECL or member.kind == CursorKind.CLASS_TEMPLATE or member.kind == CursorKind.STRUCT_DECL:
            if member.access_specifier.name.lower() == 'public' and clazz.spelling + "::" + member.spelling not in visited_classes:
                for child in member.get_children():
                    if is_variable(child) or is_method(child):
                        if classname[-1] == '_':
                            serialize_class(member,is_addon,classname[:-1])
                            visited_classes.append(classname[:-1] + "::" + member.spelling)
                        else:
                            serialize_class(member,is_addon,classname)
                            visited_classes.append(classname + "::" + member.spelling)
                        break
        elif member.kind == CursorKind.UNION_DECL:
            for union_member in member.get_children():
                if is_variable(union_member):
                    var = parse_variable(documentation_class, clazz, union_member)
                    current_variables_list.append(var)
                if union_member.kind == CursorKind.STRUCT_DECL:
                    for union_struct_member in union_member.get_children():
                        if is_variable(union_struct_member):
                            var = parse_variable(documentation_class, clazz, union_struct_member)
                            current_variables_list.append(var)
        elif is_variable(member):
            var = parse_variable(documentation_class, clazz, member)
            current_variables_list.append(var)

            #f.write( str(member.type.text) + " " + str(member.name.text) + "\n" )
        elif is_method(member):
            method = parse_function(documentation_class, clazz, member, current_methods_list)
            if method is not None:
                current_methods_list.append(method)
            else:
                methods_for_fuzzy_search.append(member)
    
    for member in methods_for_fuzzy_search:
        method = parse_function(documentation_class, clazz, member, current_methods_list, True)
        if method is not None:
            current_methods_list.append(method)
                
    
    for method in documentation_class.function_list:
        if not method in current_methods_list:
            missing_methods.append(method)
    documentation_class.function_list = current_methods_list
    
    for var in documentation_class.var_list:
        if not var in current_variables_list:
            missing_vars.append(var)
    documentation_class.var_list = current_variables_list
        
    #documentation_class.function_list.sort(key=lambda function: function.name)
    #documentation_class.var_list.sort(key=lambda variable: variable.name)
    
    if documentation_class.new:
        new_classes.append(documentation_class)
    #markdown_file.setclass(documentation_class,is_addon)

    return documentation_class.serialize()

def add_class(data, offilename):
    if offilename not in json_data:
        json_data[offilename] = {
            "name":offilename,
            #"path":name,
            "classes": [],
            "functions": []
        }
    json_data[offilename]['classes'].append(data)

def add_function(data, offilename):
    if offilename not in json_data:
        json_data[offilename] = {
            "name":offilename,
            #"path":name,
            "classes": [],
            "functions": []
        }
    json_data[offilename]['functions'].append(data)


def parse_file_child(child):
    if child.spelling.find('of')==0:
        offilename = utils.filenameFromClangChild(child)

        if utils.is_class(child):
            i=0
            for c in child.get_children():
                if utils.is_variable(c) or utils.is_method(c) or c.kind == CursorKind.CXX_BASE_SPECIFIER:
                    i+=1
            if i>0 and child.spelling not in visited_classes:
                new_class = DocClass(child)
                add_class(new_class.serialize(), offilename)
                #data['classes'].append( serialize_class(child, is_addon))
                """
                data = serialize_class(child, is_addon)
                if data is not None:
                    json_data[offilename]['classes'].append(data)

                    json_ref_data.append({
                        "file": offilename,
                        "type": "class",
                        "name": data['className']
                    })
                """
                visited_classes.append(child.spelling)

            """
           if is_function(child):
                if child.spelling not in visited_function and offilename != "ofMain":
                    visited_function.append(child.spelling)
                    json_data[offilename]['functions'].append(serialize_function(child, offilename, is_addon))
                    json_ref_data.append({
                        "file": offilename,
                        "type": "function",
                        "name": child.spelling
                    })
        """

def parse_folder(root, files, is_addon=False):
    file_count=0


    for name in files:
        file_count+=1
        filepath = os.path.join(root, name)

        if name.find('of')==0 and os.path.splitext(name)[1]=='.h':
            #print name
            #data = {
            #    "name": name,
            #    "functions" : [],
            #    "classes" : []
            #}

            tu = clang_utils.get_tu_from_file(filepath, of_root)
            for child in tu.cursor.get_children():
                parse_file_child(child)
            #functions_name = os.path.splitext(name)[0]
            #if num_functions>0 and functions_name not in visited_function_files and functions_name != "ofMain":
                #data['functions'].append(serialize_functionsfile(tu.cursor, functions_name, is_addon))
            #    visited_function_files.append(functions_name)

            #json_file.save_class(data,is_addon)

    return file_count
    
""" main """
dir_count=0
file_count=0
visited_classes = []
visited_function = []
missing_functions = []
missing_methods = []
missing_vars = []
new_classes = []
new_functions = []
new_vars = []
new_methods = []

json_data = {}
json_ref_data = []
#for root, dirs, files in os.walk(of_source):
#    dir_count+=1
#    print root, files
#    file_count += parse_folder(root, files, False)
parse_folder("/Users/jonas/Development/openframeworks/openframeworks/libs/openFrameworks/gl/", ["ofTexture.h"], False)

"""
for addon in official_addons:
    for root, dirs, files in os.walk(os.path.join(of_addons, addon, "src")):
        dir_count += 1
        file_count += parse_folder(root, files, True)
"""
for key in json_data:
    json_file.save(key,json_data[key])

json_file.save('reference',json_ref_data)

if len(new_functions)>0:
    print "added " + str(len(new_functions)) + " new functions:"
    for f in new_functions:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  to " + f.functionsfile
        
if len(missing_functions)>0:
    print "removed " + str(len(missing_functions)) + " functions"
    for f in missing_functions:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  from " + f.functionsfile

if len(new_methods)>0:
    print "added " + str(len(new_methods)) + " new methods:"
    for f in new_methods:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  to " + f.clazz
        
if len(missing_methods)>0:
    print "removed " + str(len(missing_methods)) + " methods"
    for f in missing_methods:
        print "\t- " + f.returns + " " + f.name + "(" + f.parameters + ")  from " + f.clazz

if len(new_vars)>0:
    print "added " + str(len(new_vars)) + " new vars:"
    for v in new_vars:
        print "\t- " + v.name + "  to " + v.clazz
        
if len(missing_vars)>0:
    print "removed " + str(len(missing_vars))
    for v in missing_vars:
        print "\t- " + v.name + "  from " + v.clazz
