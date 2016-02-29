from clang.cindex import CursorKind

import clang_reference
import clang_documentation_parser
import utils

class DocEnum():
    def __init__(self, cursor):
        self.cursor = cursor

        self.data = {}
        split = cursor.location.file.name.split('/')
        self.filename = split[-1]
        self.folder = self.data['folder'] = split[-2]

        self.data['name'] = cursor.spelling
        self.data['type'] = 'enum'

        # Parse documentation
        self.data['documentation'] = clang_documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False


        self.data['options'] = []
        for c in cursor.get_children():
            if c.kind == CursorKind.ENUM_CONSTANT_DECL:
                doc = clang_documentation_parser.parse_docs(c)

                if len(self.data['options']) > 0 and self.data['options'][-1]['documentation']['text'] == doc['text']:
                    doc['text'] = ''

                self.data['options'].append({
                    'name':c.spelling,
                    'value': c.enum_value,
                    'documentation': doc
                })


    def serialize(self):
        clang_reference.add_enum(self)
        return self.data
