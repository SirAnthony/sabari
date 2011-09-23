
import multiprocessing
import os
import Queue
import threading
from hashlib import sha1
from PIL import Image
from settings import IMAGES_DB
from time import sleep

try:
    from skyfront import SQL
except ImportError:
    SQL = None


class ThreadPool(multiprocessing.Process):

    def __init__(self, queue, event):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.event = event
        self.sql = None
        self.sql_queue = Queue.Queue()
        try:
            self.sql = SQL('sqlite', IMAGES_DB)
        except:
            pass

    def run(self):
        timetodie = 0
        while True:
            if self.queue.empty() and self.sql_queue.empty():
                if threading.activeCount() < 2:
                    if self.event.is_set():
                        break
                    else:
                        if timetodie > 10:
                            break
                        timetodie += 2
                        sleep(2)
            else:
                timetodie = 0
                if (threading.activeCount() - 1) < 15:
                    try:
                        ImageCreator(*(self.queue.get_nowait()),
                                        sql=self.sql_queue).start()
                    except Queue.Empty:
                        pass
                try:
                    query = self.sql_queue.get_nowait()
                    self.sql.updateRecords('images', query[0], **query[1])
                except Queue.Empty:
                        pass

class ImageCreator(threading.Thread):

    FORMATS = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'GIF': '.gif'
    }

    def __init__ (self, filename, fpath, cpath, hval, sql=None):
        threading.Thread.__init__(self)
        self.cachepath = cpath
        self.filepath = fpath
        self.filename = filename
        self.hval = hval.encode()
        self.sql = sql

    def run(self):
        maxsize = 200
        with open(os.path.join(self.filepath, self.filename)) as f:
            if self.sql:
                sha = count_hash(f)
                self.sql.put_nowait([{'filehash': sha}, {
                                    'name': self.filename,
                                    'path': self.filepath,
                                    'hash': unicode(self.hval)}])
            im = Image.open(f)
            iformat = im.format
            try:
                ext = self.FORMATS[iformat]
            except KeyError:
                ext = '.jpg'

            w,h = im.size
            if h > w:
                w = (float(w)/float(h))*maxsize
                h = maxsize
            else:
                h = (float(h)/float(w))*maxsize
                w = maxsize

            im.thumbnail((int(w),int(h)), Image.ANTIALIAS)
            try:
                im.save(self.cachepath + ext, iformat)
            except IOError, e:
                pass #print str(e)

def count_hash(f, block_size=2**20):
    sha = sha1()
    while True:
        data = f.read(block_size)
        if not data:
            break
        sha.update(data)
    f.seek(0)
    return sha.hexdigest()
