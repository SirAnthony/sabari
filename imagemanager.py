
import sqlite3

class Manager:
    def __init__(self):
        self.queries = []        
        
    def addToBase(self, name, path, sha1):
        self.queries.append('INSERT INTO `images` (name, path, sha1) VALUES ("'+name+'", "'+path+'", "'+sha1+'")')

    def commit(self, db):
        if len(self.queries):
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            for qw in self.queries:
                cursor.execute(qw)                
            conn.commit()
            cursor.close()
 

            