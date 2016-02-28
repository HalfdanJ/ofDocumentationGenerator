import markdown as markdown
import os
import shutil
import re
from sets import Set

class SiteParseMarkdown:
    outdir = ''
    markdowndir = ''
    reference = []

    global_reference = {}
    classes_reference = {}

    """
    Search for a word in global reference
    """
    def searchForGlobalReference(self, word, nextchar):
        #print classWord+" "+funcWord
        isFunction = False
        if nextchar == '(':
            isFunction = True

        if word in self.global_reference:
            item = self.global_reference[word]
            if isFunction and item['type'] == 'function':
                return item
            if not isFunction and item['type'] != 'function':
                return item

    """
    Search for a word in class reference
    """
    def searchForClassReference(self, word, nextchar, scope):
        #print word, scope, nextchar
        isFunction = False
        if nextchar == '(':
            isFunction = True

        if scope in self.classes_reference:
            if word in self.classes_reference[scope]:
                item = self.classes_reference[scope][word]
                if isFunction and item['type'] == 'function':
                    return item
                if not isFunction and item['type'] != 'function':
                    return item

    

    """
    Return a link to an item (function, var, class)
    """
    def linkToReferenceItem(self, item):
        prefix = 'global'
        if 'class' in item and item['class']:
            prefix = item['class']

        anchor = '{}_{}'.format(prefix, item['name'])

        return '<a href="{file}.html#{anchor}">{name}</a>'.format(file=item['file'], name=item['name'], anchor=anchor)

    """
    Check word if its replaceable, and return the replacing
    """
    def replaceWithLink(self, word, nextchar, scope):
        if nextchar is None:
            nextchar = ''

        # Search in global scope for matches
        ref = self.searchForGlobalReference(word, nextchar)
        if ref and ref['name'] != scope:
            return self.linkToReferenceItem(ref)+nextchar

        # Search in class scope for matches
        if scope is not None and ref is None:
            ref = self.searchForClassReference(word, nextchar, scope)
            if ref is not None and ref['name'] != scope:
                return self.linkToReferenceItem(ref)+nextchar

        # No match
        return word+nextchar


    """
    Search html for words that can be replaced with internal
    links to other documentation
    """
    def createLinks(self, html, contextClass):
        scope = None
        if contextClass['type'] == 'class':
            scope = contextClass['name']

        # Search for all words not encapsulated in <a href...
        html = re.sub(r'(?P<word>(?<!<a href=")(?<!#)\w+(?!</a>)(?!">))(?P<nextchar>\()?',
            lambda m1:
                self.replaceWithLink(m1.group('word'), m1.group('nextchar'), scope)
            , html)

        return html

    """
    Given some markdown and optional context class, return html
    """
    def parseMarkdown(self, mk, contextClass):
        if mk is None:
            return ""

        # Run markdown parser
        ret = markdown.markdown(mk, extensions=['codehilite', 'fenced_code'])
        ret = ret.replace("<code", "<code class='prettyprint lang-cpp'")

        # Images
        rx = re.compile(r"!\[.+\]\((.+)\)")
        for image in rx.finditer(ret):
            imgpath = image.group(1)
            imgpath = imgpath.replace('../','')
            dest = os.path.join(self.outdir, imgpath)

            imgpath = os.path.join(self.markdowndir, imgpath)

            if not os.path.exists(os.path.dirname(os.path.abspath(dest))):
                os.makedirs(os.path.dirname(os.path.abspath(dest)))

            if os.path.exists(imgpath) and not os.path.exists(dest):
                print "copy image  ",imgpath
                shutil.copyfile(imgpath, dest)
            #else:
            #    raise Exception('Image '+imgpath+" doesnt exist!")

        # Create links
        ret = self.createLinks(ret, contextClass)

        return ret

    def populateLookupTable(self):
        for item in self.reference:
            if 'class' in item and item['class'] and item['class'] not in self.classes_reference:
                self.classes_reference[item['class']] = {}

            if item['type'] == 'class':
                self.global_reference[item['name']] = item
            if item['type'] == 'function' or item['type'] == 'variable':
                if item['class'] is None:
                    self.global_reference[item['name']] = item
                else:
                    self.classes_reference[item['class']][item['name']] = item

        #import pprint
        #pp = pprint.PrettyPrinter(depth=6)
        #pp.pprint( self.classes_reference)
