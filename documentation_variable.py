import documentation_parser


class DocVariable():
    def __init__(self, cursor, parentclass):
        print "Parse variable "+cursor.spelling
        self.cursor = cursor

        self.data = {}
        self.data['name'] = cursor.spelling

        # Parse documentation
        self.data['documentation'] = documentation_parser.parse_docs(cursor)

        # Parse visible
        self.data['visible'] = True
        if self.data['documentation']['internal']:
            self.data['visible'] = False

        # Access
        self.data['access'] = cursor.access_specifier.name.lower()


    def serialize(self):
        return self.data