import markdown as markdown
import os
import shutil
import re

class SiteParseMarkdown:
    outdir = ''
    markdowndir = ''
    reference = []

    global_reference = {}
    classes_reference = {}


    """
    Search for a word in global reference.
    That is global functions, classes, global enums
    """
    def searchForGlobalReference(self, word, nextchar):
        #print classWord+" "+funcWord
        isFunction = False
        if nextchar == '(':
            isFunction = True

        item = None
        if word in self.global_reference:
            item = self.global_reference[word]
        elif word[-1] == 's' and word[:-1] in self.global_reference:
            item = self.global_reference[word[:-1]]

        if item:
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

    def urlToFile(self, file):
        return '{}.html'.format(file)

    def urlToReferenceItem(self, item):
        if item is None:
            return text

        name = item['name']
        if item['type'] == 'enum_option':
            name = item['enum']

        prefix = 'global'
        if 'class' in item and item['class']:
            prefix = item['class']

        return '{}.html#{}_{}'.format(item['file'], prefix, name)

    """
    Return a link to an item (function, var, class)
    """
    def linkToReferenceItem(self, item, text):
        if item is None:
            return text

        url = self.urlToReferenceItem(item)

        return '<a href="{url}">{name}</a>'.format(url=url, name=text)

    """
    Check word if its replaceable, and return the replacing
    """
    def replaceWithLink(self, word, nextchar, scope):
        if nextchar is None:
            nextchar = ''

        link_scope = scope

        scopeDecleration = re.search("(\\w+)::(\\w+)", word, re.S | re.M)
        if scopeDecleration:
            link_scope = scopeDecleration.group(1)
            word =  scopeDecleration.group(2)

        # Search in class scope for matches
        if link_scope is not None:
            ref = self.searchForClassReference(word, nextchar, link_scope)
            if ref is not None and ref['name'] != link_scope:
                if link_scope != scope:
                    word = link_scope+"::"+word
                return self.linkToReferenceItem(ref, word)+nextchar

        # Search in global scope for matches
        global_ref = self.searchForGlobalReference(word, nextchar)
        if global_ref and global_ref['name'] != scope:
            return self.linkToReferenceItem(global_ref, word)+nextchar


        # No match
        return word+nextchar


    """
    Search html for words that can be replaced with internal
    links to other documentation
    """
    def createInternalLinks(self, html, contextClass):
        scope = None
        if contextClass['type'] == 'class':
            scope = contextClass['name']

        # Search for all words not encapsulated in <a href...
        html = re.sub(r'(?P<word>(?<!<a href=")(?<!#)(?:\w+::)?\w+(?!</a>)(?!">))(?P<nextchar>\()?',
            lambda m1:
                self.replaceWithLink(m1.group('word'), m1.group('nextchar'), scope)
            , html)

        return html

    def createExternalLinks(self, html):
        html = re.sub(r'(?<!href=")(?<!">)(http[s]?://((?:[a-zA-Z]|[0-9]|[\/\-_@.&]|[!*\(\),])+))',
            lambda m1:
                '<a target="_blank" href="{}">{}</a>'.format(m1.group(1), m1.group(2))
            , html)

        return html


    def transformMarkdownToHtml(self, mk):
        ret = markdown.markdown(mk, extensions=['codehilite', 'fenced_code'])
        ret = ret.replace("<code", "<code class='prettyprint lang-cpp'")
        return ret


    """
    Given some markdown and optional context class, return html
    """
    def parseMarkdown(self, mk, contextClass):
        if mk is None:
            return ""

        # Images
        rx = re.compile(r"!\[.+\]\((.+)\)")
        for image in rx.finditer(mk):
            imgpath = image.group(1)
            imgpath = imgpath.replace('../','')
            dest = os.path.join(self.outdir, imgpath)

            imgpath = os.path.join(self.markdowndir, imgpath)

            if not os.path.exists(os.path.dirname(os.path.abspath(dest))):
                os.makedirs(os.path.dirname(os.path.abspath(dest)))

            if os.path.exists(imgpath) and not os.path.exists(dest):
                print "copy image  ",imgpath
                shutil.copyfile(imgpath, dest)
            else:
                print "Could not find "+imgpath
            #    raise Exception('Image '+imgpath+" doesnt exist!")

        # Run markdown parser
        html = self.transformMarkdownToHtml(mk)

        # Create internal links
        html = self.createInternalLinks(html, contextClass)

        # Create external links
        html = self.createExternalLinks(html)
        return html

    def populateLookupTable(self):
        for item in self.reference:
            if 'class' in item and item['class'] and item['class'] not in self.classes_reference:
                self.classes_reference[item['class']] = {}

            if item['type'] == 'function' or item['type'] == 'variable':
                if item['class'] is None:
                    self.global_reference[item['name']] = item
                else:
                    self.classes_reference[item['class']][item['name']] = item
            else:
                self.global_reference[item['name']] = item


        #import pprint
        #pp = pprint.PrettyPrinter(depth=6)
        #pp.pprint( self.classes_reference)
