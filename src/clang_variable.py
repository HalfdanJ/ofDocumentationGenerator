from clang.cindex import CursorKind

import clang_documentation_parser
import clang_reference
import utils


class DocVariable():
    def __init__(self, cursor, parentclass):
        print "Parse variable "+cursor.spelling
        self.cursor = cursor
        self.parentclass = parentclass

        self.data = {}
        self.data['name'] = cursor.spelling
        self.data['type'] = 'variable'

        split = cursor.location.file.name.split('/')
        self.filename = split[-1]
        self.data['folder'] = split[-2]

        # Parse documentation
        self.data['documentation'] = clang_documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False

        # Access
        self.data['access'] = cursor.access_specifier.name.lower()

        self.data['constant'] = cursor.result_type.is_volatile_qualified()
        self.data['static'] = cursor.kind == CursorKind.VAR_DECL
        self.data['kind'] = utils.substitutetype(cursor.type.spelling)


    def serialize(self):
        clang_reference.add_variable(self)
        return self.data
