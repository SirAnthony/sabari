# -*- coding: utf-8 -*-

import os

import Cookie
import mime
import time
import re
from hashlib import sha1
from imagemanager import Manager
from settings import ROOT, CACHE_PATH, CACHE_URL, ICONS_URL, \
                     TEMPLATE_PATH, ERROR_STYLE

from mako import exceptions
from mako.template import Template

try:
    from cache import cache, close_cache
except:
    cache = None

version = '2.0b2'

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

def pubdata():
    from urllib import unquote
    uri = unquote(os.environ.get('REQUEST_URI'))
    ctype = 'text/html'
    try:
        text = process(uri, os.environ)
    except NotFound:
        text = "Not found: '%s'" % uri
    except NotADir:
        filename = os.path.join(ROOT, uri)
        ctype = mime.guessType(uri)
        text = file(filename).read()
    except exceptions.TopLevelLookupException:
        text = "Cant find template '%s'" % uri
    except:
        if ERROR_STYLE == 'text':
            ctype = 'text/plain'
            text = exceptions.text_error_template().render()
        else:
            text = exceptions.html_error_template().render()
    print "Content-type: %s; charset=utf8\n" % ctype
    print text

def process(uri, environ):
    if uri[0] == '/':
        uri = uri[1:]
    processdir = os.path.join(ROOT, uri)
    processdirhash = sha1(processdir).hexdigest()

    if not os.path.exists(processdir):
        raise NotFound
    if os.path.isfile(processdir):
        raise NotADir

    modified = os.stat(processdir).st_mtime
    if cache:
        c = cache.get(processdirhash)
        if c and c['modified'] == modified:
            close_cache()
            data = re.sub('(?<=<span name="time">)[\d\.]+', str(Time.get()), c['data'])
            return data

    template = Template(filename=os.path.join(TEMPLATE_PATH, 'page.tpl'),
                    input_encoding='utf-8', output_encoding='utf-8')

    listing = os.listdir(processdir)
    files = []
    content = []
    images = []
    thumbs = False

    if uri and uri != '/':
        content.append({'href': '../', 'src': ICONS_URL + 'back.png',
                'alt': 'Parent', 'desc': 'Parent directory',
                'w': 165})

    try:
        cookie = Cookie.SimpleCookie()
        cookie.load(environ.get('HTTP_COOKIE'))
        cols = int(cookie.get('viewcols', 4))
    except:
        cols = 4

    for filename in listing:
        if filename.find('.') == 0:
            continue
        if os.path.isfile(os.path.join(ROOT, uri, filename)):
            files.append(filename)
        else:
            content.append({'href': os.path.join('/', uri, filename + '/').decode('utf-8'),
                            'src': ICONS_URL + 'folder.png',
                            'alt': 'Folder',
                            'desc': filename.decode('utf-8'),
                            'w': 165
            })

    for filename in files:
        if filename.find('.') == 0:
            continue
        filename = filename
        localfilename = os.path.join(uri, filename)
        filetype = mime.guessType(filename)
        fl = {'href': '/%s' % localfilename.decode('utf-8') }
        if filetype and filetype.find('image') >= 0 and filetype.find('djvu') < 0:
            #FIXME: hash for files, not for paths
            hval = sha1(localfilename).hexdigest()
            result, imtype = manager.imageProcess(hval, filename, processdir)
            fl.update({'name': hval, 'alt': 'img'})
            if result:
                fl['src'] = os.path.join(CACHE_URL, hval + imtype)
            else:
                fl['desc'] = 'Thumbinal creation.'
                thumbs = True
        else:
            if filetype:
                filetype = filetype.replace('/', '-')
            else:
                filetype = 'text-plain'
            fl.update({
                'alt': filetype,
                'src': '%s%s.png' % (ICONS_URL, filetype),
                'desc': filename.decode('utf-8'),
                'w': 165
            })
        content.append(fl)
    manager.clearOldFiles(processdir, filter(lambda x: \
                    x.has_key('alt') and x['alt'] == 'img', content))
    content.extend([None] * (cols - ((len(content) % cols) or cols)))
    content = zip(*[iter(content)]*cols)
    if template:
        rendered = template.render(version=version,
            time = Time.get(),
            path = uri.decode('utf-8'),
            items = content,
        )
        if cache and not thumbs:
            cache.set(processdirhash, {'modified': modified, 'data': rendered})
            close_cache()
        return rendered
