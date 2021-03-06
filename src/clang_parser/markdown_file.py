import os
##
## NOT IN USE
##

"""
def list_all_addons():
    modules = []
    for root, dirs, files in os.walk(documentation_root+"addons"):
        for name in dirs:
            modules.append(name)
    return set(modules)

def list_all_modules():
    modules = []
    for root, dirs, files in os.walk(documentation_root):
        for name in dirs:
            if name.find("ofx")!=0:
                modules.append(name)
    return modules

def list_all_addon_files(addon=''):
    module_files = []
    for root, dirs, files in os.walk(os.path.join(documentation_root, 'addons', addon)):
        for name in files:
            file_split = os.path.splitext(name)
            if file_split[1]=='.markdown':
                module_files.append(file_split[0])
    return module_files

def list_all_files(module=''):
    module_files = []
    for root, dirs, files in os.walk(os.path.join(documentation_root, module)):
        for name in files:
            file_split = os.path.splitext(name)
            if file_split[1]=='.markdown':
                module_files.append(file_split[0])
    return module_files
"""
def addfield(method,line):
    field = line.split(':')[0].lstrip('_').rstrip(' ')
    value = line.split(':')[1]
    if len(line.split(':'))>2:
        for text in line.split(':')[2:]:
            value = value + ":" + text

    value = value.lstrip(' ').rstrip('\n').rstrip('\r')[:-1]
    if field=='extends':
        value = value.split(", ")

    if field=='constant' or field=='advanced' or field=='visible' or field=='static' or field=='istemplated':
        value = ((value == '1') or (value == 'True') or (value=='true') or (value=='TRUE'))
    #print field, "=", value
    method[field] = value
    #setattr(method,field,value)

"""
def getfunctionsfiles_list():
    functionsfiles_list = []
    for root, dirs, files in os.walk(os.path.join(documentation_root)):
        for name in files:
            file_split = os.path.splitext(name)
            if file_split[1]=='.markdown':
                f = open(os.path.join(root,name),'rU')
                state = 'begin'
                for line in f:
                    if state == 'begin' and line.find('#functions') == 0:
                        functionsfile = file_split[0].replace('_functions','')
                        functionsfiles_list.append(functionsfile)
                        f.close()
                        break
    return functionsfiles_list
"""

def getfunctionsfile(filename,documentation_root):
    data = {
        'functions':[]
    }
    functiondata = {}
    prevBreakLine = False;
    for root, dirs, files in os.walk(os.path.join(documentation_root)):
        for name in files:
            file_split = os.path.splitext(name)
            if file_split[1]=='.markdown' and file_split[0] == filename+"_functions":
                f = open(os.path.join(root,name),'rU')
                state = 'begin'
                linenum = 0
                for line in f:
                    if state == 'begin' and line.find('#functions') == 0:
                        state = 'functionsfile'
                        data['module'] = os.path.basename(root)
                        #functionsfile.new = False

                    elif state == 'functionsfile' and line.find('_')==0:
                        addfield(data,line)

                    elif state == 'functionsfile' and line.find('##Description') == 0:
                        state = 'filedescription'
                        prevBreakLine = False

                    elif state == 'filedescription' \
                            and line.find('<!----------------------------------------------------------------------------->')==-1 \
                            and (line!='\n' or not prevBreakLine):
                        if 'description' not in data:
                            data['description'] = ''
                        data['description'] += line
                        prevBreakLine = (line=='\n')


                    elif state == 'filedescription' or state=='description' and line.find('###')==0:
                        if(state=='description'):
                            data['functions'].append(functiondata)
                        state = 'function'
                        functiondata = {}

                    elif state == 'function' and line.find('_')==0 and line.find('_inlined_description')==-1 and line.find('_description')==-1:
                        #print "##########field: " + line
                        addfield(functiondata,line)

                    elif state == 'function' and line.find('_inlined_description')==0:
                        state = 'inlined_description'
                        prevBreakLine = True

                    elif (state == 'inlined_description' or state=='function') and line.find('_description')==0:
                        state = 'description'
                        prevBreakLine = False

                    elif state == 'inlined_description' and line.find('##')!=0 and line.find('_description')==-1 and (line!='\n' or not prevBreakLine):
                        #function.inlined_description = function.inlined_description + line
                        prevBreakLine = (line=='\n')

                    elif state == 'description' \
                            and line.find('<!----------------------------------------------------------------------------->')==-1 \
                            and (line!='\n' or not prevBreakLine):

                        if 'description' not in functiondata:
                            functiondata['description'] = ''

                        functiondata['description'] += line
                        prevBreakLine = (line=='\n')

                if(state=='description'):
                    data['functions'].append(functiondata)

    #functionsfile.function_list.sort(key=lambda function: function.name)

    return data
"""
def getclass_list(documentation_root, getTemplated=True):
    class_list = []
    for root, dirs, files in os.walk(os.path.join(documentation_root)):
        for name in files:
            file_split = os.path.splitext(name)
            if file_split[1]=='.markdown':
                f = open(os.path.join(root,name),'rU')
                state = 'begin'
                for line in f:
                    if state == 'begin' and line.find('#class') == 0 and line.find(file_split[0])!=-1 :
                        if getTemplated or file_split[0][-1]!="_":
                            class_name = file_split[0]
                        elif file_split[0][-1]=="_":
                            class_name = file_split[0][:-1]
                        #print class_name
                        class_list.append(class_name)
                        f.close()
                        break
    return class_list

def sort_function(function, documentation_root):
    if (function.name==function.clazz) or (function.name == "~" + function.clazz):
        return "0" + function.name + "(" + function.parameters + ")"
    else:
        return function.name + "(" + function.parameters + ")"
"""
def getclass(clazz, documentation_root):
    data = {
        'classes':[]
    }
    method = {}
    classdata = {
        'functions':[],
        'vars':[]
    }
    var = {}
    prevBreakLine = False;
    for root, dirs, files in os.walk(os.path.join(documentation_root)):
        for name in files:
            file_split = os.path.splitext(name)
            if file_split[1]=='.markdown' and file_split[0] == clazz:
                #documentation_clazz.new = False
                f = open(os.path.join(root,name),'rU')
                state = 'begin'
                linenum = 0
                for line in f:
                    #line = line.decode("utf-8", "replace")
                    if state == 'begin' and line.find('#class') == 0 and line.find(clazz)!=-1:
                        state = 'class'
                        data['module'] = os.path.basename(root)

                    elif state == 'classdescription' and line.rstrip('\n').rstrip(' ') == '##Methods':
                        state = 'methods'

                    elif state == 'methods' and line.find('###') == 0:
                        #print "##########method: " + line
                        state = 'method'

                    elif state == 'method' and line.find('_')==0 \
                            and line.find('_description')==-1 \
                            and line.find('_inlined_description')==-1:
                        #print "##########field: " + line
                        addfield(method,line)

                    elif state == 'method' and line.find('_inlined_description')==0:
                        state = 'inlined_description'
                        prevBreakLine = False

                    elif (state == 'inlined_description' or state=='method') and line.find('_description')==0:
                        state = 'description'
                        prevBreakLine = False

                    elif state == 'inlined_description' \
                            and line.find('##')!=0 \
                            and line.find('_description')==-1 \
                            and (line!='\n' or not prevBreakLine):
                        #method.inlined_description = method.inlined_description + line
                        prevBreakLine = (line=='\n')

                    elif state == 'description' \
                            and line.find('##')!=0 \
                            and line.find('<!----------------------------------------------------------------------------->')==-1 \
                            and (line!='\n' or not prevBreakLine):
                        if 'description' not in method:
                            method['description'] = ''

                        method['description'] += line
                        prevBreakLine = (line=='\n')

                    elif state == 'description' and line.find('###') == 0:
                        state = 'method'
                        classdata['functions'].append(method)
                        method = {}
                        method['linenum'] = linenum
                        #method.file = os.path.join(root,name)

                    elif (state == 'description' or state == 'methods') \
                            and line.rstrip('\n').rstrip(' ') == '##Variables':
                        if state == 'description':
                            classdata['functions'].append(method)
                        state = 'vars'

                    elif state == 'vars' and line.find('###') == 0:
                        #print line
                        state = 'var'

                    elif state == 'var' and line.find('_')==0 and line.find('_description')==-1:
                        addfield(var,line)

                    elif state == 'var' and line.find('_description') == 0:
                        state = 'vardescription'
                        prevBreakLine = False

                    elif state == 'vardescription' \
                            and line.find('##')!=0 \
                            and line.find('<!----------------------------------------------------------------------------->')==-1 \
                            and (line!='\n' or not prevBreakLine):
                        if 'description' not in var:
                            var['description'] = ''

                        var['description'] += line
                        prevBreakLine = (line=='\n')

                    elif state == 'vardescription' and line.find('###') == 0:
                        #print line
                        state = 'var'
                        classdata['vars'].append(var)
                        var = {}
                        var['linenum'] = linenum
                        #var.file = os.path.join(root,name)

                    elif state == 'class' and line.find('_')==0:
                        addfield(classdata,line)

                    elif state == 'class' and line.find('##InlineDescription')==0:
                        state = 'classinlinedescription'
                        #documentation_clazz.detailed_inline_description = ""

                    elif state == 'classinlinedescription' \
                            and line.find('##Description')==-1 \
                            and line.find('##InlineDescription')==-1 \
                            and (line!='\n' or not prevBreakLine):
                        #documentation_clazz.detailed_inline_description  = documentation_clazz.detailed_inline_description + line
                        prevBreakLine = (line=='\n')

                    elif (state == 'classinlinedescription' or state == 'class') \
                            and line.rstrip('\n').rstrip(' ') == '##Description':
                        state = "classdescription"

                    elif state == 'classdescription' and (line!='\n' or not prevBreakLine):
                        #documentation_clazz.reference  = documentation_clazz.reference + line
                        if 'description' not in classdata:
                            classdata['description'] = ''

                        classdata['description'] += line

                        prevBreakLine = (line=='\n')

                    linenum = linenum + 1
                if state == 'vardescription':
                    classdata['vars'].append(var)

                f.close()
    return classdata

"""


def serialize_function(f,function,member):
    f.write('###' + function.returns + " " + function.syntax + "\n\n")
    f.write("<!--\n");
    f.write("_syntax: " + function.syntax + "_\n")
    f.write("_name: " + function.name + "_\n")
    f.write("_returns: " + function.returns + "_\n")
    f.write("_returns_description: " + function.returns_description + "_\n")
    f.write("_parameters: " + function.parameters + "_\n")
    if(member):
        f.write("_access: " + function.access + "_\n")
    f.write("_version_started: " + function.version_started + "_\n")
    f.write("_version_deprecated: " + function.version_deprecated + "_\n")
    f.write("_summary: " + function.summary + "_\n")
    f.write("_constant: " + str(function.constant) + "_\n")
    f.write("_static: " + str(function.static) + "_\n")
    f.write("_visible: " + str(function.visible) + "_\n")
    f.write("_advanced: " + str(function.advanced)  + "_\n")
    f.write("-->\n\n");
    f.write("_inlined_description: _\n\n")
    f.write(function.inlined_description.strip("\n").decode('utf-8').encode('utf-8'))
    f.write('\n\n\n\n\n\n')
    f.write("_description: _\n\n")
    f.write(function.description.strip("\n").encode('utf-8'))
    f.write('\n\n\n\n\n\n')
    f.write('<!----------------------------------------------------------------------------->\n\n')

def serialize_var(f,var):
    f.write('###' + var.type + " " + var.name + "\n\n")
    f.write("<!--\n");
    f.write("_name: " + var.name + "_\n")
    f.write("_type: " + var.type + "_\n")
    f.write("_access: " + var.access + "_\n")
    f.write("_version_started: " + var.version_started + "_\n")
    f.write("_version_deprecated: " + var.version_deprecated + "_\n")
    f.write("_summary: " + var.summary + "_\n")
    f.write("_visible: " + str(var.visible) + "_\n")
    f.write("_constant: " + str(var.constant) + "_\n")
    f.write("_advanced: " + str(var.advanced) + "_\n")
    f.write("-->\n\n");
    f.write("_inlined_description: _\n\n")
    f.write(var.inlined_description.strip("\n").decode('utf-8').encode('utf-8'))
    f.write('\n\n\n\n\n\n')
    f.write("_description: _\n\n")
    f.write(var.description.strip("\n").encode('utf-8'))
    f.write("\n\n\n\n\n\n")
    f.write('<!----------------------------------------------------------------------------->\n\n')

def setclass(clazz,is_addon=False):
    path = ""
    if is_addon:
        path = os.path.join(documentation_root,"addons",clazz.module)
    else:
        path = os.path.join(documentation_root,clazz.module)

    try:
        os.mkdir(path)
    except:
        pass

    f = open(os.path.join(path,clazz.name)+".markdown",'w')
    f.write('#class ' + clazz.name + '\n\n\n')
    f.write("<!--\n");
    f.write("_visible: " + str(clazz.visible) + "_\n")
    f.write("_advanced: " + str(clazz.advanced) + "_\n")
    f.write("_istemplated: " + str(clazz.istemplated) + "_\n")
    f.write("_extends: " + ", ".join(clazz.extends) + "_\n")
    f.write("-->\n\n");

    #f.write('//----------------------\n\n')
    #f.write('##Example\n\n' + clazz.example + '\n\n\n\n')
    f.write('##InlineDescription\n\n' + clazz.detailed_inline_description.decode('utf-8').encode('utf-8') + '\n\n\n\n')

    #f.write('//----------------------\n\n')
    f.write('##Description\n\n' + clazz.reference.encode('utf-8') + '\n\n\n\n')

    #f.write('//----------------------\n\n')
    f.write('##Methods\n\n\n\n')

    #f.write('//----------------------\n\n')
    for method in clazz.function_list:
        serialize_function(f,method,True)

    f.write('##Variables\n\n\n\n')

    #f.write('//----------------------\n\n')
    for var in clazz.var_list:
        serialize_var(f,var)
    f.close()
    return

def setfunctionsfile(functionfile,is_addon=False):
    path = ""
    if is_addon:
        path = os.path.join(documentation_root,"addons",functionfile.module)
    else:
        path = os.path.join(documentation_root,functionfile.module)

    try:
        os.mkdir(path)
    except:
        pass

    f = open(os.path.join(path,functionfile.name)+"_functions.markdown",'w')
    f.write('#functions\n\n\n')
    f.write("<!--\n");
    f.write("_visible: " + str(functionfile.visible) + "_\n")
    f.write("_advanced: " + str(functionfile.advanced) + "_\n")
    f.write("-->\n\n");
    f.write('##Description\n\n' + functionfile.description + '\n\n\n\n')

    f.write('<!----------------------------------------------------------------------------->\n\n')
    for function in functionfile.function_list:
        if function.name.find('OF_DEPRECATED_MSG')==-1:
            serialize_function(f,function,False)
"""
