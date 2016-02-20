import os

import re
from clang.cindex import CursorKind


def is_class(member):
    return member.kind == CursorKind.CLASS_DECL or member.kind == CursorKind.CLASS_TEMPLATE or member.kind == CursorKind.STRUCT_DECL

def is_variable(member):
    return member.kind == CursorKind.VAR_DECL or member.kind == CursorKind.FIELD_DECL

def is_method(member):
    return member.kind == CursorKind.CXX_METHOD or member.kind == CursorKind.CONSTRUCTOR or member.kind == CursorKind.DESTRUCTOR or member.kind == CursorKind.FUNCTION_TEMPLATE

def is_function(member):
    return (member.kind == CursorKind.FUNCTION_DECL or member.kind == CursorKind.FUNCTION_TEMPLATE) and not is_class(member.semantic_parent)

def filenameFromClangChild(child):
    return os.path.basename(child.location.file.name).split('.')[0]


def substitutetype(ty):
    """ fix types to match the standard format in the final docs,
        removes std:: and adds a leading and trailing space between
        triangular brackets """

    ty = ty.replace("std::", "")
    ty = re.sub(r"(.*)<(.*)>","\\1< \\2 >",ty)
    return ty
