import markdown as markdown
import os
import shutil
import re

class SiteParseMarkdown:
    outdir = ''
    markdowndir = ''

    def parseMarkdown(self, mk):
        if mk is None:
            return ""
        ret = markdown.markdown(mk, extensions=['codehilite', 'fenced_code'])
        ret = ret.replace("<code", "<code class='prettyprint lang-cpp'")

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
            #else:
            #    raise Exception('Image '+imgpath+" doesnt exist!")



        return ret
