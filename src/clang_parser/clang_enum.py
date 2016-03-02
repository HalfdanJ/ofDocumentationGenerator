from clang.cindex import CursorKind

import clang_reference
import clang_documentation_parser
from clang_base_type import DocBase

class DocEnum(DocBase):
    def __init__(self, cursor):
        DocBase.__init__(self, cursor)

        self.data['type'] = 'enum'

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
