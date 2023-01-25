import hashlib

class Block:
    def __init__(self):
        self.index = 0
        self.previousHash = 0
        self.listOfTransactions = []
        self.hash = '0'

    def setHash(self):
        self.hash = hashlib.sha256(str(self.index).encode('utf-8') + str(self.previousHash) + str(self.listOfTransactions).encode('utf-8')).hexdigest()