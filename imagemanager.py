
from skyfront import SQL

db = os.path.join(os.getcwd(), 'images.sqlite')

class Manager:
    def __init__(self):
        self.sql = SQL('sqlite', db)

    def addToBase(self, name, path, sha1):
        self.sql.insertNew('images', name=name, path=path, hash=sha1)

    def removeFromBase(self, name, path, sha1):
        self.sql.delete('images', name=name, path=path, hash=sha1)

    def setupDB():
        if not os.path.exists(db):
            open(path,'w').close()
        self.sql = SQL('sqlite', db)
        self.sql.executeQuery("""CREATE TABLE IF NOT EXISTS `images` (
                                id INTEGER PRIMARY KEY autoincrement,
                                name VARCHAR NOT NULL,
                                path VARCHAR NOT NULL,
                                hash VARCHAR NOT NULL)""")
        #self.sql.executeQuery("""CREATE TABLE IF NOT EXISTS `tags` (
        #                        id INTEGER PRIMARY KEY autoincrement,
        #                        hash VARCHAR NOT NULL,
        #                        tag VARCHAR NOT NULL)""")
