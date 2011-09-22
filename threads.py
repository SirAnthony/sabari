
import multiprocessing
import os
import Queue
import threading
from PIL import Image
from time import sleep


class ThreadPool(multiprocessing.Process):

    def __init__(self, queue, event):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.event = event

    def run(self):
        timetodie = 0
        while True:
            if self.queue.empty():
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
                        ImageCreator(*(self.queue.get_nowait())).start()
                    except Queue.Empty:
                        pass

class ImageCreator(threading.Thread):

    FORMATS = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'GIF': '.gif'
    }

    def __init__ (self, filename, fpath, spath):
        threading.Thread.__init__(self)
        self.spath = spath
        self.filepath = fpath
        self.filename = filename

    def run(self):
        maxsize = 200
        with open(os.path.join(self.filepath, self.filename)) as f:
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
                im.save(self.spath + ext, iformat)
            except IOError, e:
                pass #print str(e)
