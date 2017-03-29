import MySQLdb
import re


class Database:
    configPath = 'dbconfig.mems'
    host = ""
    db = ""
    password = ""
    user = ""

    def __init__(self):
        try:
            with open(self.configPath, 'r') as f:
                for line in f:
                    if re.search('host', line):
                        temp = re.split('=', line)[1]
                        self.host = re.sub("\n", "", temp)
                    if re.search('db', line):
                        temp = re.split('=', line)[1]
                        self.db = re.sub("\n", "", temp)
                    if re.search('password', line):
                        temp = re.split('=', line)[1]
                        self.password = re.sub("\n", "", temp)
                    if re.search('user', line):
                        temp = re.split('=', line)[1]
                        self.user = re.sub("\n", "", temp)
        except:
            f = open(self.configPath, 'w')
            f.write("host=\ndb=\npassword=\nuser=")
            f.close()

    def configuration(self):
        conf = 'host: ' + self.host + '\ndb: ' + self.db + '\nuser: ' + self.user + '\npass: ' + self.password
        print(conf)

    def select(self, sql):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db)
        cursor = db.cursor()

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
        except:
            results = -1

        db.close()
        return results

    def insert(self, sql):
        db = MySQLdb.connect(self.host, self.user, self.password, self.db)
        cursor = db.cursor()
        print("hallo")
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        db.close()