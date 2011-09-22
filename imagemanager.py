
import os
from multiprocessing import Queue, Event
from settings import IMAGES_DB, CACHE_PATH
from threads import ThreadPool

try:
    from skyfront import SQL
except ImportError:
    SQL = None

class Manager:

    def __init__(self):
        if not SQL:
            return
        self.sql = SQL('sqlite', IMAGES_DB)
        self.pool = None

    def createMaker(self):
        if self.pool and pool.is_active():
            return
        self.__image_queue = Queue()
        self.__image_event = Event()
        self.pool = ThreadPool(self.__image_queue, self.__image_event)
        self.pool.start()

    def killMaker(self):
        self.__image_event.set()
        self.pool = None

    def __del__(self):
        self.killMaker()

    def imageProcess(self, hval, filename, path):
        cpath = os.path.join(CACHE_PATH, hval)
        for ext in ('.jpg', '.jpeg', '.png', '.gif'):
            if os.path.isfile(cpath + ext):
                return True, ext
        self.createMaker()
        self.__image_queue.put_nowait([filename, path, cpath])
        self.addToBase(filename, path, hval)
        return None, None

    def addToBase(self, name, path, sha1):
        if not SQL:
            return
        self.sql.insertNew('images', name=name.decode('utf-8'),
                                     path=path.decode('utf-8'),
                                     hash=sha1.decode('utf-8'))

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
                ext = record[1].rsplit(u'.', 1)[-1]
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
