import hashlib

class Blockchain:
    def __init__(self,previous_block_hash,transaction_list):
            self.previous_block_hash=previous_block_hash
            self.transaction_list=transaction_list

            self.block_data="-".join(transaction_list)+"-"+previous_block_hash
            self.block_hash=hashlib.sha256(self.block_data.encode()).hexdigest()

t1='Anna sent 5SC to Adam'
t2='Sebastian sent 32SC to Conrad'
t3='Dominic sent 54SC to Adrian'
t4='Andrew sent 56SC to Michael'
t5='Patricia sent 44SC to Agnieszka'
t6='Mark sent 56SC to Zuckerberg'
initial_block=Blockchain("Initial String",[t1,t2])

print(initial_block.block_data)
print(initial_block.block_hash)

second_block=Blockchain(initial_block,[t3,t4])

print(initial_block.block_data)
print(initial_block.block_hash)

third_block=Blockchain(second_block,[t5,t6])
print(initial_block.block_data)
print(initial_block.block_hash)