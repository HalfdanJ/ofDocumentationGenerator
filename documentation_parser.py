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
        "parameters": {},
        "returns": None,
        "sa": [],
        "internal": False,
        "warning": None,
        "deprecated": None
    }

    doc = str("" if element.raw_comment is None else element.raw_comment).strip()
    mode = 'text'
    for line in iter(doc.splitlines()):
        line = line.strip()
        parammatch = re.search("///\s*(\\\\(\w+))", line, re.I | re.S)
        linematch = re.search("///\s*(\\\\(\w+)\s)?(.*)$", line, re.I | re.S)

        if linematch:
            text = linematch.group(3)
            param = None
            if parammatch:
                param = parammatch.group(2)

            if param is not None:
                param = param.lower()
                if param == 'brief':
                    ret['text'] += text+"\n"
                    mode = 'text'
                elif param == 'returns':
                    ret['returns'] = text
                    mode = 'returns'
                elif param == 'param' or param == 'tparam':
                    paramSearch = re.search("(\\w+)\\s(.*)", text, re.I | re.S)
                    if paramSearch:
                        ret['parameters'][paramSearch.group(1)] = paramSearch.group(2)
                elif param == 'sa' or param == 'see':
                    ret['sa'].append(text)
                elif param == 'warning':
                    ret['warning'] = text
                    mode = 'warning'
                elif param == 'note':
                    ret['text'] += "Note: "+text+"\n"
                    mode = 'text'
                elif param == 'deprecated':
                    ret['deprecated'] = text
                elif param == 'internal':
                    ret['internal'] = True
                elif param == 'section':
                    ret['section'] = text

                else:
                    print "MISSINGPARAM"
                    print param + " | "+ text
            else:
                ret[mode] += text+"\n"


        else:
            print "NO MATCH "+line

    return ret
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