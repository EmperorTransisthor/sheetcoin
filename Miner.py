#TODO: Marcin Wojtowicz 
import multiprocessing
import hashlib
NONCE_LIMIT=2**23
zeroes=4
def mine(block_number,transactions,previous_hash):
    for nonce in range(NONCE_LIMIT):
        base_text=str(block_number)+transactions+previous_hash+str(nonce)
        hash_try=hashlib.sha256(base_text.encode()).hexdigest()
        if hash_try.startswith('0'*zeroes):
            print(f"Found Hash With Nonce: {nonce}")
            return hash_try
    return -1
block_number=24

#previous_hash=
mine(block_number,transactions,previous_hash)