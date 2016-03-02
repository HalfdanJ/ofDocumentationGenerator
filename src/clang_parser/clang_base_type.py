import clang_documentation_parser

class DocBase():
    def __init__(self, cursor):
        self.data = {}
        self.cursor = cursor

        split = cursor.location.file.name.split('/')
        self.data['filename'] = self.filename = split[-1]
        self.data['folder']   = self.folder = split[-2]
        self.data['line'] = cursor.location.line

        self.data['name'] = self.name = cursor.spelling

        # Parse documentation
        self.data['documentation'] = clang_documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False
