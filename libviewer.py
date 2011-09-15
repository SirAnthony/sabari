
import os
import mimetypes
import hashlib
from PIL import Image
import time
from threading import Thread, Lock
import Cookie
from imagemanager import Manager

from mako import exceptions
from mako.template import Template

import cgi

try:
    import cache
except:
    cache = None

version = 1.99

root = '/'
error_style = 'html'

manager = Manager()

class Time:
    time = time.time()
    @classmethod
    def get(cls):
        return time.time() - cls.time
    @classmethod
    def now(cls):
        cls.time = time.time()

def serve(environ, start_response):
    """serves requests using the WSGI callable interface."""
    Time.now()
    fieldstorage = cgi.FieldStorage(
            fp = environ['wsgi.input'],
            environ = environ,
            keep_blank_values = True
    )
    d = dict([(k, getfield(fieldstorage[k])) for k in fieldstorage])

    uri = environ.get('PATH_INFO', '/')
    try:
        tmpl = process(uri, environ)
        start_response("200 OK", [('Content-type','text/html')])
        return [tmpl]
    except exceptions.TopLevelLookupException:
        start_response("404 Not Found", [])
        return ["Cant find template '%s'" % uri]
    except:
        if error_style == 'text':
            start_response("200 OK", [('Content-type','text/plain')])
            return [exceptions.text_error_template().render()]
        else:
            start_response("200 OK", [('Content-type','text/html')])
            return [exceptions.html_error_template().render()]

def pubdata(form):
    uri = form.get('d')
    try:
        text = process(uri, os.environ)
    except:
        if error_style == 'text':
            start_response("200 OK", [('Content-type','text/plain')])
            text = exceptions.text_error_template().render()
        else:
            start_response("200 OK", [('Content-type','text/html')])
            text = exceptions.html_error_template().render()
    print "Content-type: text/html; charset=utf8\n\n";
    print text

def process(uri, environ):
    cookie = Cookie.SimpleCookie()
    try:
        cookie.load(environ.get('HTTP_COOKIE'))
    except:
        pass
    template = Template(filename=os.path.join(os.getcwd(), 'page.tpl'),
                        input_encoding='utf-8')
    processdir = os.path.join(root, uri)
    localfilename = os.path.join(uri, filename)
    modified = os.stat(processdir).st_mtime
    if cache:
        c = cache.get(processdir)
        if c and c['modified'] == modified:
            return c['data']
    mimetypes.init()
    listing = os.listdir(processdir)
    files = []
    content = []
    if uri and uri != '/':
        content.append({'href': '..', 'img': '/icon/back.png',
                'alt': 'Parent', 'desc': 'Parent directory'})
    try:
        cols = int(cookie.get('viewcols', 4))
    except:
        cols = 4
    for filename in listing:
        if filename.find('.') == 0: continue
        if os.path.isfile(os.path.join(root, uri, filename)):
            files.append(filename)
        else:
            content.append({'href': localfilename,
                            'img': '/icon/folder.png',
                            'alt': 'Folder',
                            'desc': filename
            })
    for filename in files:
        if filename.find('.') == 0:
            continue
        filetype = mimetypes.guess_type(filename)[0]
        fl = {'href': localfilename}
        if filetype and filetype.find('image') >= 0 and filetype.find('djvu') < 0:
            hval = hashlib.sha1(localfilename).hexdigest()
            result, imtype = imagework(hval, filename, processdir)
            if result:
                fl['src'] = '/cache/' + hval + imtype
                fl['name'] = hval
                fl['alt'] = 'img'
            else:
                fl['desc'] = 'Thumbinal creation.'
        else:
            if filetype:
                filetype = filetype.replace('/', '-')
            else:
                filetype = 'text-plain'
            fl['alt'] = filetype
            fl['src'] = '/icon/%s.png' % filetype
            fl['desc'] = filename
        content.append(fl)
    content.extend([None] * (cols - ((len(content) % cols) or cols)))
    content = zip(*[iter(content)]*cols)
    if template:
        rendered = template.render(version=version,
            time = Time.get(),
            path = uri,
            items = content,
        ).encode('utf-8')
        if cache:
            cache.set(processdir, {'modified': modified, 'data': rendered})
        return rendered

class ImageCreator(Thread):

    lock = Lock()

    def __init__ (self, filename, fpath, spath):
        Thread.__init__(self)
        self.spath = spath
        self.filepath = fpath
        self.filename = filename

    def run(self):
        maxsize = 200
        ext = '.jpg'
        with open(os.path.join(self.filepath, self.filename)) as f:
            im = Image.open(f)
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
            #TODO: debug
            except IOError: return
            sha1 = hashlib.sha1(f.read()).hexdigest()
            with self.lock:
                manager.addToBase(self.filename, self.filepath, sha1)

def imagework(hval, filename, path):
    cpath = './cache/' + hval
    for ext in ('.jpg', 'jpg', '.png', '.gif'):
        if os.path.isfile(cpath + ext):
            return True, ext
    ImageCreator(filename, path, cpath).start()
    return None, None
