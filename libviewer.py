
import os

import Cookie
import hashlib
import mime
import time
import re
from imagemanager import Manager, ImageCreator
from settings import ROOT, CACHE_PATH, ERROR_STYLE

from mako import exceptions
from mako.template import Template

try:
    from cache import cache, close_cache
except:
    cache = None

version = '2.0a1'

manager = Manager()

class Time:
    time = time.time()
    @classmethod
    def get(cls):
        return time.time() - cls.time
    @classmethod
    def now(cls):
        cls.time = time.time()

class NotFound(OSError):
    pass
class NotADir(OSError):
    pass

def serve(environ, start_response):
    """serves requests using the WSGI callable interface."""
    Time.now()

    uri = environ.get('PATH_INFO', '/')

    try:
        tmpl = process(uri, environ)
        start_response("200 OK", [('Content-type','text/html')])
        return [tmpl]
    except NotFound:
        start_response("404 Not Found", [])
        return ["Not found: '%s'" % uri]
    except NotADir:
        filename = os.path.join(ROOT, uri)
        start_response("200 OK", [('Content-type', mime.guessType(uri))])
        return [file(filename).read()]
    except exceptions.TopLevelLookupException:
        start_response("404 Not Found", [])
        return ["Cant find template '%s'" % uri]
    except:
        if ERROR_STYLE == 'text':
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
        if ERROR_STYLE == 'text':
            start_response("200 OK", [('Content-type','text/plain')])
            text = exceptions.text_error_template().render()
        else:
            start_response("200 OK", [('Content-type','text/html')])
            text = exceptions.html_error_template().render()
    print "Content-type: text/html; charset=utf8\n\n";
    print text

def process(uri, environ):
    processdir = os.path.join(ROOT, uri)
    if not os.path.exists(processdir):
        raise NotFound
    if os.path.isfile(processdir):
        raise NotADir

    modified = os.stat(processdir).st_mtime
    if cache:
        c = cache.get(processdir)
        if c and c['modified'] == modified:
            close_cache()
            data = re.sub('(?<=<span name="time">)[\d\.]+', str(Time.get()), c['data'])
            return data

    cookie = Cookie.SimpleCookie()
    try:
        cookie.load(environ.get('HTTP_COOKIE'))
    except:
        pass
    template = Template(filename=os.path.join(os.getcwd(), 'page.tpl'),
                    input_encoding='utf-8')
    print 'Creation'
    listing = os.listdir(processdir)
    files = []
    content = []
    images = []
    thumbs = False
    if uri and uri != '/':
        content.append({'href': u'../', 'img': u'/icon/back.png',
                'alt': u'Parent', 'desc': u'Parent directory'})
    try:
        cols = int(cookie.get('viewcols', 4))
    except:
        cols = 4
    for filename in listing:
        if filename.find('.') == 0:
            continue
        if os.path.isfile(os.path.join(ROOT, uri, filename)):
            files.append(filename)
        else:
            content.append({'href': os.path.join(uri, filename + u'/').decode('utf-8'),
                            'img': u'/icon/folder.png',
                            'alt': u'Folder',
                            'desc': filename.decode('utf-8')
            })
    for filename in files:
        if filename.find('.') == 0:
            continue
        filename = filename.decode('utf-8')
        localfilename = os.path.join(uri, filename)
        filetype = mime.guessType(filename)
        fl = {'href': localfilename}
        if filetype and filetype.find('image') >= 0 and filetype.find('djvu') < 0:
            #FIXME: hash for files, not for paths
            hval = hashlib.sha1(localfilename.encode('utf-8')).hexdigest().decode('utf-8')
            result, imtype = imagework(hval, filename, processdir)
            fl.update({'name': hval, 'alt': u'img'})
            if result:
                fl['src'] = os.path.join(CACHE_PATH, hval + imtype)
            else:
                fl['desc'] = u'Thumbinal creation.'
                thumbs = True
        else:
            if filetype:
                filetype = filetype.replace('/', '-')
            else:
                filetype = 'text-plain'
            fl['alt'] = filetype
            fl['src'] = u'/icon/%s.png' % filetype
            fl['desc'] = filename
        content.append(fl)
    manager.clearOldFiles(processdir, filter(lambda x: \
                    x.has_key('alt') and x['alt'] == 'img', content))
    content.extend([None] * (cols - ((len(content) % cols) or cols)))
    content = zip(*[iter(content)]*cols)
    if template:
        rendered = template.render(version=version,
            time = Time.get(),
            path = uri,
            items = content,
        ).encode('utf-8')
        if cache and not thumbs:
            cache.set(processdir, {'modified': modified, 'data': rendered})
            close_cache()
        return rendered

def imagework(hval, filename, path):
    cpath = os.path.join(CACHE_PATH, hval)
    for ext in ('.jpg', '.jpeg', '.png', '.gif'):
        if os.path.isfile(cpath + ext):
            return True, ext
    ImageCreator(filename, path, cpath).start()
    manager.addToBase(filename, path, hval)
    return None, None
