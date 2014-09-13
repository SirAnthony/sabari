
import os
import mimetypes
import hashlib
from PIL import Image
import time
from threading import Thread

ver = 1.99

part = '/var/www/site'

starttime = time.time()

def putdata(form):
    if form.has_key('d'):
        value = form['d'].value
        mimetypes.init()
        print "Content-type: text/html; charset=utf8\n\n";
        print '''
<html>
	<head>
		<title>Index of %s</title>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<link href="/styles/mainst.css" rel="stylesheet" type="text/css">
		<style>a img{border: 0px;}</style>
	</head>
	<body>
		<h1>Index of %s</h1>
		<hr>
		<table>
		    <tr>
		        <td class="t1" valign="top" align="center" >
			        <a href=".."><img src="/icon/back.png" width="165" height="165" alt="Parent"><br>Parent Directory</a>
		        </td>
''' % (value, value)
        content = os.listdir(part+value)
        files = []
        td, tr = 1, 0
        cols = 4
        for filename in content:
            if filename.find('.') == 0: continue
            if os.path.isfile(part+value+'/'+filename):
                files.append(filename)
            else:
                if td > cols: td = 0
                print '<td class="%s" valign="top" align="center">' % td
                print '<a href="%s/"><img src="/icon/folder.png" width="165" height="165" alt="Dir">' % (os.path.join(value,filename))
                print '<br>%s</a></td>' % filename
                if td == cols: print '</tr><tr>'
                td += 1
        for filename in files:
            #if filename.find('.') == 0: continue
            if td > cols: td = 0
            filetype = mimetypes.guess_type(filename)[0]
            print '<td class="t%s" valign="top" align="center">' % td
            print '<a href="%s" target="_blank">' % (os.path.join(value,filename))
            if filetype and filetype.find('image') >= 0 and filetype.find('djvu') < 0:
                hval = hashlib.md5(os.path.join(value,filename)).hexdigest()
                result, imtype = imagework(hval, os.path.join(part+value ,filename))                
                if result == 'ext':
                    print '<img src="/cache/%s" alt="img">' % (hval + imtype)
                else:
                    print 'Thumbinal created.';
            else:
                if filetype:
                    filetype = filetype.replace('/', '-')
                else:
                    filetype = 'text-plain'
                print '<img src="/icon/%s.png" width="165" height="165"><br>%s' % (filetype, filename)
            print '</a></td>'
            if td == cols: print '</tr><tr>'
            td += 1
        print '''</tr>
</table><hr><p class="ft">
Sabari v %s<br>
Time: %0.5f s.<br>
Original <a href="http://code.google.com/p/sabari/">script</a> by 
<a href="mailto:anthony@adsorbtion.org\">Sir Anthony</a></p>
''' % (ver, time.time() - starttime)

class ImageCreator(Thread):

    def __init__ (self, filename, spath):
        Thread.__init__(self)
        self.spath = spath
        self.filename = filename

    def run(self):
        maxsize = 200
        ext = '.jpg'
        im = Image.open(self.filename)
        format = im.format        
        if not format: format = 'JPEG'
        if format == 'PNG': ext = '.png'
        if format == 'GIF': ext = '.gif'
        w,h = im.size
        if h > w:
            w = (float(w)/float(h))*maxsize
            h = maxsize
        else:
            h = (float(h)/float(w))*maxsize
            w = maxsize
        im.thumbnail((int(w),int(h)), Image.ANTIALIAS)
        try: im.save(self.spath + ext, format)
        except IOError: pass

def imagework(hval, filename):
    cpath = '/var/www/cache/' + hval
    for ext in ('.jpg', '.png', '.gif'):
        if os.path.isfile(cpath + ext):
            return 'ext', ext
    ImageCreator(filename, cpath).start()
    return 'crt', None

