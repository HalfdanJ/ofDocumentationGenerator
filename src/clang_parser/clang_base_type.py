import clang_documentation_parser

class DocBase():
    def __init__(self, cursor, of_root):
        self.data = {}
        self.cursor = cursor

        self.data['file'] = cursor.location.file.name.replace(of_root, '', 1)

        split = cursor.location.file.name.split('/')
        self.data['filename'] = self.filename   = split[-1]
        self.data['folder']   = self.folder     = split[-2]

        # Addons should take parents parents folder name
        if self.folder == 'src' and self.data['file'].startswith('/addons'):
            self.data['folder']   = self.folder     = split[-3]

        self.data['line']                       = cursor.location.line

        self.data['name']     = self.name       = cursor.spelling

        # Parse documentation
        self.data['documentation'] = clang_documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False
