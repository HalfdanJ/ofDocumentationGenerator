import re

from clang.cindex import CursorKind

import documentation_parser
import utils
import documentation_reference

class DocFunction():
    def __init__(self, cursor, parentclass):
        print "Parse function " + cursor.spelling
        self.cursor = cursor
        self.parentclass = parentclass

        self.data = {}
        self.data['name'] = cursor.spelling
        self.data['name'] = re.sub("<.*>", "", self.data['name'])

        # Parse documentation
        self.data['documentation'] = documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False

        # Access
        self.data['access'] = cursor.access_specifier.name.lower()

        # Static
        self.data['static'] = cursor.is_static_method()

        # Returns
        if cursor.kind == CursorKind.CONSTRUCTOR or cursor.kind == CursorKind.DESTRUCTOR or (
            not parentclass is None and self.data['name'] == parentclass.name):
            returns = ""
        else:
            returns = utils.substitutetype(cursor.result_type.spelling)
            returns = ("" if returns is None else returns)

        self.data['returns'] = returns

        # parameters
        self.data['deprecated'] = False
        self.parse_parameters()

    def parse_parameters(self):
        self.data['parameters'] = []

        # Parse the arguments into a stirng
        for arg in self.cursor.get_children():
            if arg.kind.is_attribute():
                # TODO: we suppose only attributes are the deprecated ones
                self.data['deprecated'] = True
                return
            if arg.kind != CursorKind.PARM_DECL:
                continue

            argtype = utils.substitutetype(arg.type.spelling)
            if argtype[-1] == '&' or argtype[-1] == '*':
                self.data['parameters'].append(argtype + arg.spelling)
            else:
                self.data['parameters'].append(argtype + " " + arg.spelling)

            try:
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

                        self.data['parameters'][-1] += "=" + part.get_tokens().next().spelling
                    elif part.kind == CursorKind.DECL_REF_EXPR:
                        self.data['parameters'][-1] += "=" + part.spelling
            except:
                pass

    def serialize(self):
        documentation_reference.add_function(self)
        return self.data
