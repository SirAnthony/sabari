
import os
from PIL import Image
from settings import IMAGES_DB, CACHE_PATH
from threading import Thread, Lock

try:
    from skyfront import SQL
except ImportError:
    SQL = None

class ImageCreator(Thread):

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
            try:
                im.save(self.spath + ext, format)
            except IOError, e:
                pass #print str(e)


class Manager:
    def __init__(self):
        if not SQL:
            return
        self.sql = SQL('sqlite', IMAGES_DB)

    def addToBase(self, name, path, sha1):
        if not SQL:
            return
        self.sql.insertNew('images', name=name, path=path, hash=sha1)

    def clearOldFiles(self, path, files):
        if not SQL:
            return
        status, data = self.sql.getRecords('images', ['hash', 'id', 'name'],
                                            path=path.decode('utf-8'))
        records = {}
        if status:
            for elem in data:
                records[elem[0]] = elem[1:]
            for fileinfo in files:
                try:
                    del records[fileinfo['name']]
                except KeyError:
                    pass
            for rname in records.keys():
                record = records[rname]
                self.sql.delete('images', id=record[0])
                ext = record[1].rsplit('.', 1)[-1]
                if ext == 'jpeg':
                    ext = 'jpg'
                os.unlink(os.path.join(CACHE_PATH, '%s.%s' % (rname, ext)))

    def removeFromBase(self, name, path, sha1):
        if not SQL:
            return
        self.sql.delete('images', name=name, path=path, hash=sha1)

    def setupDB(self):
        if not SQL:
            return
        if not os.path.exists(IMAGES_DB):
            open(IMAGES_DB,'w').close()
            self.sql = SQL('sqlite', IMAGES_DB)
        print self.sql.executeQuery("""CREATE TABLE IF NOT EXISTS `images` (
                            id INTEGER PRIMARY KEY autoincrement,
                            name VARCHAR NOT NULL,
                            path VARCHAR NOT NULL,
                            hash VARCHAR NOT NULL,
                            UNIQUE (name, path))""")
        #self.sql.executeQuery("""CREATE TABLE IF NOT EXISTS `tags` (
        #                        id INTEGER PRIMARY KEY autoincrement,
        #                        hash VARCHAR NOT NULL,
        #                        tag VARCHAR NOT NULL)""")

    def dropDB(self):
        if not SQL:
            return
        print self.sql.executeQuery('DROP TABLE `images`')
        #self.sql.executeQuery('DROP TABLE `tags`')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        m = Manager()
        if sys.argv[1] == 'setup':
            print 'Installing database.'
            m.setupDB()
        if sys.argv[1] == 'dropdb':
            print 'Cleaning database.'
            m.dropDB()
