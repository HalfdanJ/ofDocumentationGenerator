from clang.cindex import CursorKind

import clang_reference
import clang_utils

from clang_function import DocFunction
from clang_variable import DocVariable
from clang_base_type import DocBase


class DocClass(DocBase):
    def __init__(self, cursor, of_root):
        DocBase.__init__(self, cursor, of_root)

        self.data['type'] = 'class'

        # Parse extends
        self.data['extends'] = []

        for child in cursor.get_children():
            if child.kind == CursorKind.CXX_BASE_SPECIFIER:
                if child.spelling.find("class") == 0:
                    baseclass = child.spelling.split(' ')[1]
                    self.data['extends'].append(baseclass)
                else:
                    self.data['extends'].append(child.spelling)

        # Parse member children
        self.member_variables = []
        self.member_functions = []

        for member in cursor.get_children():
            # Struct decleration
            # TODO
            if member.kind == CursorKind.CLASS_DECL or member.kind == CursorKind.CLASS_TEMPLATE or member.kind == CursorKind.STRUCT_DECL:
                if member.access_specifier.name.lower() == 'public':
                    for child in member.get_children():
                        if clang_utils.is_variable(child) or clang_utils.is_method(child):
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
                    if clang_utils.is_variable(union_member):
                        #print "UNION "+union_member.spelling

                        #var = parse_variable(documentation_class, clazz, union_member)
                        #current_variables_list.append(var)
                    if union_member.kind == CursorKind.STRUCT_DECL:
                        for union_struct_member in union_member.get_children():
                            if clang_utils.is_variable(union_struct_member):
                                #print "UNION "+union_struct_member.spelling

                                #var = parse_variable(documentation_class, clazz, union_struct_member)
                                #current_variables_list.append(var)
                    """

            elif clang_utils.is_variable(member):
                if member.access_specifier.name.lower() == 'public':
                    var = DocVariable(member, self, of_root)
                    self.member_variables.append(var)

                #f.write( str(member.type.text) + " " + str(member.name.text) + "\n" )
            elif clang_utils.is_method(member):
                func = DocFunction(member, self, of_root)
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

        clang_reference.add_class(self)

        return self.data
