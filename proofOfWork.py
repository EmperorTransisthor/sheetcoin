import hashlib
import time
from multiprocessing import Process
from multiprocessing import Value
from clientUtils import send_all, receive_all
max_nonce = 2 ** 32 # 4 billion
diff=10
# custom process class
class ProofOfWork(Process):
    # override the constructor
    def __init__(self,difficulty_bits,header):
        # execute the base constructor
        Process.__init__(self,difficulty_bits,header)
        # initialize integer attribute
        self.difficulty_bits=difficulty_bits
        self.header=header
        self.hash_result = Value('c','a')
        self.nonce=Value('i',0)
 
    # override the run function
    def proof_of_work(self):
        target = 2 ** (256-self.difficulty_bits)
        for self.nonce.value in range(max_nonce):
            str_out = hashlib.sha256(str(self.header).encode('utf-8') + str(self.nonce.value).encode('utf-8')).hexdigest()
            # check if this is a valid result, below the target
            if int(str_out, 16) < target:
                self.hash_result.value=str_out
                print(f"Success with nonce {self.nonce.value}")
                print(f'Hash is {self.hash_result.value}')
                return True
        print(f'Failed after {self.nonce.value} tries')
        return False
 
class Blockchain:
    def __init__(self,previous_block_hash,transaction_list):
            self.previous_block_hash=previous_block_hash
            self.transaction_list=transaction_list

            self.block_data="-".join(transaction_list)+"-"+previous_block_hash
            self.block_hash=hashlib.sha256(self.block_data.encode()).hexdigest()
            
def CheckTheNode(hashedheader):
    # Check the node and add to blockchain (USECASE 1)
    if int(hashedheader, 16) < 2 ** (256-diff):
        print(f"Correct")
        return Blockchain("Initial string",hashedheader)
    print('Cheater')
    return None

#Mining:usecase 3
def SetWork(message,ip,_port,privateKey):
    nonce = 0
    hash_result = ''
    p = ProofOfWork(diff,message)
    p.start()
    #in that moment, the server should wait for reply from
    #other nodes
    
    p.join()

    #kill processes as soon as the node gets answer
    p.kill()#on windows p.terminate()
    #p.nonce.value
    
    if(p.header.value!='a'):#Send correct solution to nodes for check
        send_all(ip, _port, privateKey, p.header.value)

    # difficulty from 0 to 24 bits
    #for difficulty_bits in range(24):
       # difficulty = 2 ** difficulty_bits
     #   print(f'Difficulty: {difficulty} ({difficulty_bits})')
      #  print('Starting search...')
        # checkpoint the current time
       # start_time = time.time()
        # make a new block which includes the hash from the previous block
        # we fake a block of transactions - just a string
        #new_block = 'test block with transactions' + hash_result
        # find a valid nonce for the new block
        #(hash_result, nonce) = proof_of_work(new_block, difficulty_bits)
        # checkpoint how long it took to find a result
       # end_time = time.time()
        # elapsed_time = end_time - start_time
        # print('Elapsed Time: %.4f seconds' % elapsed_time)
        # if elapsed_time > 0:
        #     # estimate the hashes per second
        #     hash_power = float(nonce / elapsed_time)
        #     print('Hashing Power: %ld hashes per second' % hash_power)