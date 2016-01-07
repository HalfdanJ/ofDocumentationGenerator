import HTMLParser
import re


def parse_sections(element):
    """ looks for \section element in documentation block  """
    doc = str("" if element.raw_comment is None else element.raw_comment)
    doc = doc.strip()
    for line in iter(doc.splitlines()):
        line = line.strip()
        section_index = line.lower().find("\\section");
        if(section_index != -1):
            section_name = line[(section_index+len("\\section")):].strip()
            return section_name

    return None


def parse_docs(element):
    """ parse an inlined documentation block """
    ret = {
        "text": "",
        "section": None,

    }

    doc = str("" if element.raw_comment is None else element.raw_comment).strip()

    #for line in iter(doc.splitlines()):
    #    ret.text

    if doc.find("< ") == 0:
        doc = doc[2:]
    if doc.find("\\todo") == 0:
        doc = ""
    if doc.find("\\tparam") == 0:
        doc = re.sub(r"\\tparam.*","",doc)
    if doc.find("TODO:") == 0:
        doc = ""
    doc = doc.replace("\\warning ","\nWarning: ")
    doc = doc.replace("\\author ","\nBy: ")
    doc = doc.replace("\\param ","\nParameters:\n",1)
    doc = doc.replace("\\param ","")
    doc = doc.replace("\\brief ","")
    doc = doc.replace("\\returns ","\nReturns: ")
    doc = doc.replace("\\sa ","\nSee also: ")
    doc = doc.replace("\\note ","\nNote: ")
    docs = ""
    for line in iter(doc.splitlines()):
        line = line.strip()
        line = line.replace("/// ","")
        line = line.replace("///","")
        line = re.sub(r"\\class (.*)","",line)

        if(line.lower().find("\\section") != -1):
            continue
        if(line.lower().find("\\cond") != -1):
            continue

        docs += line + "\n"

    try:
        docs = HTMLParser.HTMLParser().unescape(docs)
    except:
        pass
    docs = docs.strip()
    return docs