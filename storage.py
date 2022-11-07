from flask import jsonify

class Storage:
    storage = {}        # ip+port : publicKey

    def push(self, ip, port, publicKey):
        element = {}
        element[(ip, port)] = publicKey
        self.storage.update(element)

    def get(self, ip, port):
        return self.storage(ip, port)

    def getStorage(self):
        return self.storage

    def getStorage_json(self):
        storedNodes = {}
        for i in self.storage:
            ip, port = i
            url = str(ip) + ":" + str(port)
            publicKey = self.storage[i]
            storedNodes.update[url] = publicKey
        
        return storedNodes

    def print(self):
        for i in self.storage:
            ip, port = i
            print("address: " + str(ip) + ":" + str(port) + "\npublicKey: " + self.storage[i])
