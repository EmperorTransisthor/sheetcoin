import hashlib
import json
import time

class Blockchain:
   
    # This function is created
    # to create the very first
    # block and set its hash to "0"
    def __init__(self):
        self.chain = []
        self.createBlock(previousHash='0', listOfTransactions=[])
 
    # This function is created
    # to add further blocks
    # into the chain
    def createBlock(self, listOfTransactions, previousHash):
        block = {'blockIndex': len(self.chain) + 1,
                 'listOfTransactions': listOfTransactions,
                 'timestamp': time.time(),
                 'previousHash': previousHash}
        block['hash'] = self.hash(block)
        self.chain.append(block)
        return block
       
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