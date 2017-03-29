import re
import database


class Agent:
    configPath = "agconfig.mems"
    id = ""
    func = ""

    def __init__(self, db):
        self.database = db

        try:
            f = open(self.configPath, 'r')
            for line in f:
                if re.search('id', line):
                    temp = re.split('=', line)
                    self.id = re.sub('\n', '', temp)
                if re.search('func', line):
                    temp = re.split('=', line)
                    self.func = re.sub('\n', '', temp)

            f.close()

        except:
            f = open(self.configPath, 'w')
            f.write('id=\nname=none\nuser_id=\nfunction_id=5')
            f.close()

    def configuration(self):
        conf = 'id: ' + self.id + "\nfunc: " + self.func
        print(conf)

    def sendmessage(self, frame, receiver, mes):
        sql = "INSERT INTO \
               messages(sender_id, receiver_id, message_type_id, frame, status) \
               VALUES ('%d', '%d', '%d', '%s', '%s')" % \
               (1, receiver, mes, frame, 'send')

        print(sql)
        self.database.insert(sql)
