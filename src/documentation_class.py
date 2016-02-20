#!/usr/bin/python
# import documentation_functions
from clang.cindex import CursorKind

import documentation_parser
import documentation_reference
import utils
from documentation_function import DocFunction

import re
import Levenshtein

from documentation_variable import DocVariable


class DocClass:
    def __init__(self, cursor):
        print "Parse class "+cursor.spelling
        self.cursor = cursor

        self.data = {}
        self.name = self.data['name'] = cursor.spelling

        split = cursor.location.file.name.split('/')
        self.filename = split[-1]
        self.folder = split[-2]


        # Parse extends
        self.data['extends'] = []
        for child in cursor.get_children():
            if child.kind == CursorKind.CXX_BASE_SPECIFIER:
                if child.spelling.find("class") == 0:
                    baseclass = child.spelling.split(' ')[1]
                    self.data['extends'].append(baseclass)
                else:
                    self.data['extends'].append(child.spelling)

        # Parse documentation
        self.data['documentation'] = documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False

        # Parse member children
        self.member_variables = []
        self.member_functions = []

        for member in cursor.get_children():

            # Struct decleration
            # TODO
            if member.kind == CursorKind.CLASS_DECL or member.kind == CursorKind.CLASS_TEMPLATE or member.kind == CursorKind.STRUCT_DECL:
                if member.access_specifier.name.lower() == 'public':
                    for child in member.get_children():
                        if utils.is_variable(child) or utils.is_method(child):
                            #print "MEMBER"+member.spelling
                            """if classname[-1] == '_':
                                serialize_class(member,is_addon,classname[:-1])
                                visited_classes.append(classname[:-1] + "::" + member.spelling)
                            else:
                                serialize_class(member,is_addon,classname)
                                visited_classes.append(classname + "::" + member.spelling)
                            break"""

            # Union decleration
            # TODO
            elif member.kind == CursorKind.UNION_DECL:
                for union_member in member.get_children():
                    """
                    if utils.is_variable(union_member):
                        #print "UNION "+union_member.spelling

                        #var = parse_variable(documentation_class, clazz, union_member)
                        #current_variables_list.append(var)
                    if union_member.kind == CursorKind.STRUCT_DECL:
                        for union_struct_member in union_member.get_children():
                            if utils.is_variable(union_struct_member):
                                #print "UNION "+union_struct_member.spelling

                                #var = parse_variable(documentation_class, clazz, union_struct_member)
                                #current_variables_list.append(var)
                    """

            elif utils.is_variable(member):
                if member.access_specifier.name.lower() == 'public':
                    var = DocVariable(member, self)
                    self.member_variables.append(var)

                #f.write( str(member.type.text) + " " + str(member.name.text) + "\n" )
            elif utils.is_method(member):
                func = DocFunction(member, self)
                self.member_functions.append(func)
                """
                method = parse_function(documentation_class, clazz, member, current_methods_list)
                if method is not None:
                    current_methods_list.append(method)
                else:
                    methods_for_fuzzy_search.append(member)
                """


    def serialize(self):
        self.data['member_variables'] = []
        self.data['methods'] = []

        for var in self.member_variables:
            self.data['member_variables'].append(var.serialize())

        for func in self.member_functions:
            self.data['methods'].append(func.serialize())

        documentation_reference.add_class(self)

        return self.data
"""
    def get_parameter_types(self, parameters_list):
        parameters_types = []
        if len(parameters_list.strip(' ')) == 0:
            return parameters_types
        for p in parameters_list.split(','):
            parameter = ""
            for e in p.split(' ')[:len(p.split(' ')) - 1]:
                parameter = parameter + " " + e
            parameters_types.append(parameter)
        return parameters_types

    def get_parameter_names(self, parameters_list):
        parameters_names = []
        if len(parameters_list.strip(' ')) == 0:
            return parameters_names
        for p in parameters_list.split(','):
            p = p.strip(' ')
            if p.find('=') != -1:
                e = p.split('=')[0].strip(' ')
                parameters_names.append(e.split(' ')[len(e.split(' ')) - 1] + ' = ' + p.split('=')[1])
            else:
                parameters_names.append(p.split(' ')[len(p.split(' ')) - 1])
        return parameters_names


    def fuzzy_function_search(self, name, returns, parameters, alternatives, already_found):
        most_similar_function = None
        max_similarity = 0
        for function in self.function_list:
            if function in already_found:
                continue
            if function.name == name:
                dst_parameters_types = self.get_parameter_types(function.parameters)
                src_parameters_types = self.get_parameter_types(parameters)
                if len(src_parameters_types) == len(dst_parameters_types):
                    a = -1
                    for i in range(len(src_parameters_types)):
                        ty = src_parameters_types[i].strip()
                        other_ty = dst_parameters_types[i].strip()
                        non_const_ty = re.sub(r"const (.*)", "\\1", ty).strip()
                        non_const_other_ty = re.sub(r"const (.*)", "\\1", other_ty).strip()
                        if ty != other_ty and \
                                not self.test_alternative_types(ty, other_ty, alternatives) and \
                                        non_const_ty != other_ty and \
                                not self.test_alternative_types(non_const_ty, other_ty, alternatives) and \
                                        non_const_ty != non_const_other_ty and \
                                not self.test_alternative_types(non_const_ty, non_const_other_ty, alternatives) and \
                                        ty != non_const_other_ty and \
                                not self.test_alternative_types(ty, non_const_other_ty, alternatives):
                            non_const_ty = re.sub(r"(.*)::(.*)", "\\2", non_const_ty).strip()
                            if ty != other_ty and \
                                    not self.test_alternative_types(ty, other_ty, alternatives) and \
                                            non_const_ty != other_ty and \
                                    not self.test_alternative_types(non_const_ty, other_ty, alternatives) and \
                                            non_const_ty != non_const_other_ty and \
                                    not self.test_alternative_types(non_const_ty, non_const_other_ty, alternatives) and \
                                            ty != non_const_other_ty and \
                                    not self.test_alternative_types(ty, non_const_other_ty, alternatives):
                                break
                        else:
                            a = i
                    fuzzy_return = returns.replace("&", "").replace("*", "").strip()
                    other_fuzzy_return = function.returns.replace("&", "").replace("*", "").strip()
                    non_const_return = re.sub(r"const (.*)", "\\1", fuzzy_return).strip()
                    non_const_other_return = re.sub(r"const (.*)", "\\1", other_fuzzy_return).strip()
                    if a == len(src_parameters_types) - 1 and \
                            (fuzzy_return == other_fuzzy_return or \
                                     self.test_alternative_types(fuzzy_return, other_fuzzy_return, alternatives) or \
                                         fuzzy_return == non_const_other_return or \
                                     self.test_alternative_types(fuzzy_return, non_const_other_return, alternatives) or \
                                         non_const_return == non_const_other_return or \
                                     self.test_alternative_types(non_const_return, non_const_other_return,
                                                                 alternatives) or \
                                         non_const_return == other_fuzzy_return or \
                                     self.test_alternative_types(non_const_return, other_fuzzy_return, alternatives)):
                        function.new = False
                        return function
                if most_similar_function == None or Levenshtein.ratio(parameters,
                                                                      str(function.parameters)) > max_similarity:
                    most_similar_function = function
        return most_similar_function

    def function_by_signature(self, name, returns, parameters, alternatives, already_found, fuzzy):
        method = DocsMethod(0)
        method.name = name
        method.parameters = parameters
        method.syntax = name + "("
        for p in self.get_parameter_names(parameters):
            method.syntax = method.syntax + p + ", "
        method.syntax = method.syntax.rstrip(', ')
        method.syntax = method.syntax + ")"
        method.returns = returns
        method.new = True
        for function in self.function_list:
            if function.name == name:
                dst_parameters_types = self.get_parameter_types(function.parameters)
                src_parameters_types = self.get_parameter_types(parameters)
                if (len(src_parameters_types) == len(dst_parameters_types)):
                    a = -1
                    for i in range(len(src_parameters_types)):
                        if src_parameters_types[i] != dst_parameters_types[i]:
                            break
                        else:
                            a = i
                    if a == len(src_parameters_types) - 1 and function.returns == returns:
                        function.new = False
                        function.parameters = parameters
                        function.syntax = method.syntax
                        function.returns = method.returns
                        return function
        if fuzzy and len(alternatives) > 0:
            alternative_func = self.fuzzy_function_search(name, returns, parameters, alternatives, already_found)
            if alternative_func != None:
                alternative_func.parameters = method.parameters
                alternative_func.syntax = method.syntax
                alternative_func.returns = method.returns
                return alternative_func
            else:
                self.function_list.append(method)
                return method
        else:
            return None

    def var_by_name(self, name):
        for var in self.var_list:
            if var.name == name:
                return var
        return False

    def get_inlined_docs_similarity(self):
        return Levenshtein.ratio(self.detailed_inline_description, self.reference)

    def is_class(self):
        return True

"""