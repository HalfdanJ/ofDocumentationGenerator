import markdown as markdown
import os
import shutil
import re

class SiteParseMarkdown:
    outdir = ''
    markdowndir = ''
    reference = []

    def searchForGlobalReference(self, classWord, funcWord):
        #print classWord+" "+funcWord
        isFunction = False
        if funcWord[-1] == '(':
            funcWord = funcWord[0:-1]
            isFunction = True

        for item in self.reference:
            if isFunction and item['type'] == 'function' and item['class'] is None:
                if item['name'] == funcWord:
                    return item

            if not isFunction and item['type'] == 'class':
                if item['name'] == funcWord:
                    return item


    def searchForClassReference(self, classWord, funcWord, scope):

        isFunction = False
        if funcWord[-1] == '(':
            funcWord = funcWord[0:-1]
            isFunction = True

        for item in self.reference:
            if isFunction and item['type'] == 'function' and item['class'] == scope:
                if item['name'] == funcWord:
                    return item

            if not isFunction and item['type'] == 'variable' and item['class'] == scope:
                if item['name'] == funcWord:
                    return item

    def linkToReferenceItem(self, item):
        return item['file']+".html"+"#"+item['name']

    def replaceWithLink(self, html, ref):
        link = self.linkToReferenceItem(ref)

        # Pattern that tries to not match elements that already are in links
        pattern = re.compile("(?<!href=\")"+ref['name']+"(?!\">)(?!</a>)")

        ret = pattern.sub('<a href="'+link+'">'+ref['name']+'</a>', html)
        return ret

    def replaceLinks(self, html, contextClass):
        scope = None
        if contextClass['type'] == 'class':
            scope = contextClass['name']

        # Check all text to see if its refering to something in reference
        pattern = re.compile(r'((\w+)\.)?(\w+\(?)')
        for (_word1, classWord, funcWord) in re.findall(pattern, html):
            ref = self.searchForGlobalReference(classWord, funcWord)
            if ref is not None and (scope is None or ref['name'] != scope):
                html = self.replaceWithLink(html, ref)

            if scope is not None and ref is None:
                ref = self.searchForClassReference(classWord, funcWord, scope)
                if ref is not None and ['name'] != scope:
                    html = self.replaceWithLink(html, ref)


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
