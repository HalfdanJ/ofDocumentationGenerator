import markdown as markdown
import os
import shutil
import re

class SiteParseMarkdown:
    outdir = ''
    markdowndir = ''
    reference = []

    def searchForGlobalReference(self, word, nextchar):
        #print classWord+" "+funcWord
        isFunction = False
        if nextchar == '(':
            isFunction = True

        for item in self.reference:
            if isFunction and item['type'] == 'function' and item['class'] is None:
                if item['name'] == word:
                    return item

            if not isFunction and item['type'] == 'class':
                if item['name'] == word:
                    return item


    def searchForClassReference(self, word, nextchar, scope):
        #print word, scope, nextchar
        isFunction = False
        if nextchar == '(':
            isFunction = True

        for item in self.reference:
            if isFunction and item['type'] == 'function' and item['class'] == scope:
                if item['name'] == word:
                    return item

            if not isFunction and item['type'] == 'variable' and item['class'] == scope:
                if item['name'] == word:
                    return item

    def linkToReferenceItem(self, item):
        prefix = 'global'
        if 'class' in item and item['class']:
            prefix = item['class']

        anchor = '{}_{}'.format(prefix, item['name'])

        return '<a href="{file}.html#{anchor}">{name}</a>'.format(file=item['file'], name=item['name'], anchor=anchor)

    def replaceWithLink(self, word, nextchar, scope):
        if nextchar is None:
            nextchar = ''

        ref = self.searchForGlobalReference(word, nextchar)
        if ref and ref['name'] != scope:
            return self.linkToReferenceItem(ref)+nextchar

        if scope is not None and ref is None:
            ref = self.searchForClassReference(word, nextchar, scope)
            if ref is not None and ref['name'] != scope:
                return self.linkToReferenceItem(ref)+nextchar

        return word+nextchar



    def replaceLinks(self, html, contextClass):
        scope = None
        if contextClass['type'] == 'class':
            scope = contextClass['name']

        # Search for all words not encapsulated in <a href...
        html = re.sub(r'(?P<word>(?<!<a href=")(?<!#)\w+(?!</a>)(?!">))(?P<nextchar>\()?',
            lambda m1:
                self.replaceWithLink(m1.group('word'), m1.group('nextchar'), scope)
            , html)

        """
        pattern = re.compile(r'((\w+)\.)?(\w+?)')
        for (_word1, classWord, funcWord) in re.findall(pattern, html):
            ref = self.searchForGlobalReference(classWord, funcWord)
            if ref is not None and (scope is None or ref['name'] != scope):
                html = self.replaceWithLink(html, ref)

            if scope is not None and ref is None:
                ref = self.searchForClassReference(classWord, funcWord, scope)
                if ref is not None and ['name'] != scope:
                    html = self.replaceWithLink(html, ref)
        """


        return html


    def parseMarkdown(self, mk, contextClass):

        #print scope
        if mk is None:
            return ""


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

        ret = self.replaceLinks(ret, contextClass)




        #
        #         print funcWord
        #     #print word1+"  "+word2+"  "+word3


        return ret
