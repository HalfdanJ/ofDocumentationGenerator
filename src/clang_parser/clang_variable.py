from clang.cindex import CursorKind

import clang_reference
import clang_utils
from clang_base_type import DocBase


class DocVariable(DocBase):
    def __init__(self, cursor, parentclass, of_root):
        DocBase.__init__(self, cursor, of_root)

        self.parentclass = parentclass

        self.data['type'] = 'variable'

        # Access
        self.data['access'] = cursor.access_specifier.name.lower()

        self.data['constant'] = cursor.result_type.is_volatile_qualified()
        self.data['static'] = cursor.kind == CursorKind.VAR_DECL
        self.data['kind'] = clang_utils.substitutetype(cursor.type.spelling)

    def serialize(self):
        clang_reference.add_variable(self)
        return self.data
