
import os
from PIL import Image
from skyfront import SQL
from threading import Thread, Lock

db = os.path.join(os.getcwd(), 'images.sqlite')

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
            try: im.save(self.spath + ext, format)
            #TODO: debug
            except IOError, e:
                print

class Manager:
    def __init__(self):
        self.sql = SQL('sqlite', db)

    def addToBase(self, name, path, sha1):
        print self.sql.insertNew('images', name=name, path=path, hash=sha1)

    def clearOldFiles(self, path, files):
        status, records = self.sql.getRecords('images', ['hash', 'id'], path=path)
        if status:
            records = dict(records)
            for fileinfo in files:
                try:
                    del records[fileinfo['name']]
                except KeyError:
                    pass
            for f in records.values():
                self.sql.delete('images', id=f)

    def removeFromBase(self, name, path, sha1):
        self.sql.delete('images', name=name, path=path, hash=sha1)

    def setupDB(self):
        if not os.path.exists(db):
            open(db,'w').close()
            self.sql = SQL('sqlite', db)
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
