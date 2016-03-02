import clang_reference
from clang_base_type import DocBase

class DocTypedef(DocBase):
    def __init__(self, cursor):
        DocBase.__init__(self, cursor)

        self.data['type'] = 'typedef'
        self.data['typedef_type'] = cursor.underlying_typedef_type.spelling

    def serialize(self):
        clang_reference.add_typedef(self)
        return self.data
