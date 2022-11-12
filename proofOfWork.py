import hashlib
import time

max_nonce = 2 ** 32 # 4 billion

def proof_of_work(header, difficulty_bits):
    # calculate the difficulty target
    target = 2 ** (256-difficulty_bits)
    for nonce in range(max_nonce):
        hash_result = hashlib.sha256(str(header).encode('utf-8') + str(nonce).encode('utf-8')).hexdigest()
        # check if this is a valid result, below the target
        if int(hash_result, 16) < target:
            print(f"Success with nonce {nonce}")
            print(f'Hash is {hash_result}')
            return (hash_result,nonce)
    print(f'Failed after {nonce} tries')
    return nonce

if __name__ == '__main__':
    nonce = 0
    hash_result = ''
    # difficulty from 0 to 24 bits
    for difficulty_bits in range(24):
        difficulty = 2 ** difficulty_bits
        print(f'Difficulty: {difficulty} ({difficulty_bits})')
        print('Starting search...')
        # checkpoint the current time
        start_time = time.time()
        # make a new block which includes the hash from the previous block
        # we fake a block of transactions - just a string
        new_block = 'test block with transactions' + hash_result
        # find a valid nonce for the new block
        (hash_result, nonce) = proof_of_work(new_block, difficulty_bits)
        # checkpoint how long it took to find a result
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('Elapsed Time: %.4f seconds' % elapsed_time)
        if elapsed_time > 0:
            # estimate the hashes per second
            hash_power = float(nonce / elapsed_time)
            print('Hashing Power: %ld hashes per second' % hash_power)