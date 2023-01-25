import hashlib
import json
import time

class Blockchain:

    def __init__(self):
        self.nodeBalance = 0.0
        self.userWallets = {}
        self.chain = []
        self.currentTransactions = []
        self.createBlock(previousHash='0', listOfTransactions=[])
 
    def createBlock(self, previousHash, proof): #TODO(EmperorTransisthor): Should we rename previousHash variable?
        """ Adds block to blockchain

        Args:
            `previousHash` -> `String`: previously calculated hash in hexadecimal format
            `proof` -> `String`: proof of work
        Returns:
            `block` -> `dict`: current block structure
        """

        block = {'index': len(self.chain) + 1,
                 'transactions': self.currentTransactions,
                 'proof': proof,
                 'timestamp': time.time(),
                 'previousHash': previousHash}
        self.currentTransactions = []
        self.chain.append(block)
        return block

    def createTransaction(self, sender, recipient, transactionAmount):
        """ Adds transaction to transaction pool

        Args:
            `sender` -> `String`: transaction sender
            `recipient` -> `String`: transaction recipient
            `transactionAmount` -> `float`: transaction amount
        Returns:
            `block` -> `dict`: current block structure
        """

        if sender not in self.userWallets:
            self.userWallets[sender] = 0
        if recipient not in self.userWallets:
            self.userWallets[recipient] = 0

        tax = transactionAmount * 0.05
        totalAmount = transactionAmount + tax

        if self.userWallets[sender] < totalAmount:
            raise Exception ("Insufficient funds")

        self.userWallets[sender] -= totalAmount
        self.userWallets[recipient] += transactionAmount
        self.nodeBalance += tax

        self.currentTransactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': transactionAmount,
        })
        return self.getPreviousBlock['index'] + 1
       
    # This function is created
    # to display the previous block
    def getPreviousBlock(self):
        return self.chain[-1]
       
    # This is the function for proof of work
    # and used to successfully mine the block
    # def proof_of_work(self, previous_proof):
    #     new_proof = 1
    #     check_proof = False
         
    #     while check_proof is False:
    #         hash_operation = hashlib.sha256(
    #             str(new_proof**2 - previous_proof**2).encode()).hexdigest()
    #         if hash_operation[:5] == '00000':
    #             check_proof = True
    #         else:
    #             new_proof += 1
                 
    #     return new_proof
 
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
 

    # def chain_valid(self, chain):
    #     previous_block = chain[0]
    #     block_index = 1
         
    #     while block_index < len(chain):
    #         block = chain[block_index]
    #         if block['previousHash'] != self.hash(previous_block):
    #             return False
               
    #         previous_proof = previous_block['proof']
    #         proof = block['proof']
    #         hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
             
    #         if hash_operation[:4] != '0000':
    #             return False
    #         previous_block = block
    #         block_index += 1
         
    #     return True