import ecdsa
import sys
import getopt
import hashlib
import json
from requests import post
from time import sleep
from hashlib import sha3_512
from hashlib import sha256
from time import time


wallet = {
"John":63.5,
"Andrew":980.0,
"Mark":400.0,
"Juliette":5.0,
"Steven":0.0
}
PREFIX_ZEROS = '0000'
DIFFICULTY_BITS = 14
MAX_NONCE = 2**32

def pushNewNodeToStorage(request, storage):
    """ Add new node IP, port and publicKey to storage.

    Args:
        `request` -> `flask.request`: request received.
        `storage` -> `Storage`: storage with nodes.
    """

    remoteIp = request.get_json()['ip']
    remotePort = request.get_json()['port']
    remotePublicKey = request.get_json()['publicKey']
    storage.push(remoteIp, remotePort, remotePublicKey)
    print("Succesfully registered " + str(remoteIp) + ":" + str(remotePort))

def getAllNodes(storage, ip, port, publicKey):
    """ Return all nodes with host node.

    Args:
        `storage` -> `Storage`: storage with nodes.
        `ip` -> `String`: host IP
        `port` -> `String`: host port
        `publicKey` -> `String`: host publicKey in hexadecimal format
    Returns:
        `nodes` -> `dict`: dictionary of nodes info including host
    """

    nodes = {}
    nodes[(ip, port)] = publicKey
    nodes.update(storage.getStorage())
    return nodes

def sendAllNodes(storage, request):
    """ Send info about all nodes to newly registered node.

    Args:
        `request` -> `flask.request`: request received.
        `storage` -> `Storage`: storage with nodes.
    """

    sleep(2)
    print("sending all nodes")
    remoteIp = request.get_json()['ip']
    remotePort = request.get_json()['port']
    for i in storage:
        sleep(1)
        ip, port = i
        publicKey = storage[i]
        url = "http://" + str(remoteIp) + ":" + str(remotePort) + "/register"
        message = {
                "ip": ip,
                "port": port,
                "publicKey": publicKey
            }
        post(url, json=message)

def messageAll(request, storage):
    """ Spread out received message to all nodes in the network.

    Args:
        `request` -> `flask.request`: request received.
        `storage` -> `Storage`: storage with nodes.
    """

    targetIp = request.get_json()['ip']
    targetPort = request.get_json()['port']
    targetNodes = {}
    targetNodes.update(storage.getStorage())
    targetNodes.pop((targetIp, targetPort))
    for i in targetNodes:
        ip, port = i
        message = {
            "ip": targetIp,
            "port": targetPort,
            "payload": request.get_json()['payload'],
            "signature": request.get_json()['signature']
        }
        url = "http://" + formatUrl(ip, port) + "/receive_from"
        print(url)
        post(url, json = message)

def sendMineCommandToAll(request, storage):
    """ Spread out received message to all nodes in the network.

    Args:
        `request` -> `flask.request`: request received.
        `storage` -> `Storage`: storage with nodes.
    """
    targetIp = request.get_json()['ip']
    targetPort = request.get_json()['port']
    targetNodes = {}
    targetNodes.update(storage.getStorage())
    targetNodes.pop((targetIp, targetPort))
    for i in targetNodes:
        ip, port = i
        message = {
            "ip": targetIp,
            "port": targetPort,
            "payload": request.get_json()["payload"],
            "signature": request.get_json()['signature']
        }
        url = "http://" + formatUrl(ip, port) + "/receive_mine"
        print(url)
        post(url, json = message)

def proofOfWork(queue, blockchain, listOfTransactions):
    nonce = 0
    hash_result = ''
    # difficulty from 0 to 24 bits
    # for difficulty_bits in range(24):
        # difficulty = 2 ** difficulty_bits
        # print(f'Difficulty: {difficulty} ({difficulty_bits})')
    out = queue.get()
    
    print('Starting search...')
    # make a new block which includes the hash from the previous block
    blockchain.createBlock(blockchain.getPreviousBlock()['previousHash'], 'p') # FIXME(EmperorTransisthor): proofOfWork 'p'

    # find a valid nonce for the new block
    (hash_result, nonce) = findHashNonce(listOfTransactions, blockchain.getPreviousBlock()['previousHash'], blockchain.getPreviousBlock()['index'])
    out['hash'] = hash_result
    out['nonce']=nonce
    queue.put(out)
    #return results to validate in other nodes
    return nonce, hash_result

def findHashNonce(listOfTransactions, previousHash, index):
    #  here we set how long it can search nonce
    max_nonce = 2 ** 32
    start_time = time()
    for nonce in range(max_nonce):
        hash_result = sha256(str(listOfTransactions).encode('utf-8') + str(index).encode('utf-8') + str(nonce).encode('utf-8') + str(previousHash).encode('utf-8')).hexdigest()
        target = 2 ** (256 - DIFFICULTY_BITS)
        if int(hash_result, 16) < target:
            end_time = time()
            elapsed_time = end_time - start_time
            hash_power = float(nonce / elapsed_time)
            print(f"Success with nonce {nonce}")
            print(f'Hash is {hash_result}')
            print('Elapsed Time: %.4f seconds' % elapsed_time)
            print('Hashing Power: %ld hashes per second' % hash_power)
            return (hash_result,nonce)
    print(f'Failed after {nonce} tries')
    return -1

def isFork(validatedHash, blockchain,currTimestamp):
    prev_hash=blockchain.getPreviousBlock()['previousHash']
    prev_timestamp=blockchain.getPreviousBlock()['timestamp']
    if (currTimestamp-prev_timestamp<10.0):
                print('Fork attempt!')
                print('---'+prev_hash)
                print('|')
                print('---'+validatedHash)
                print('Pushing to orphan!')
                return True
    return False

def validation(nonce, hashToValidate, blockchain,currTimestamp):
    previous_block = blockchain.getPreviousBlock()
    print("previous hash: " + str(blockchain.getPreviousBlock()['previousHash']))
    print("hash to validate: " + str(hashToValidate))
    print("len first: " + str(len(previous_block['previousHash'])))
    print("len second: "+ str(len(hashToValidate)))
    #FIXME(EmperorTransisthor): ?
    if len(previous_block['previousHash']) != len(hashToValidate) or isFork(hashToValidate, blockchain,currTimestamp):
        return False

    return True

    
    

def validateToAll(request, storage, nonce, hashToValiate):
    """ Spread out received message to all nodes in the network.

    Args:
        `request` -> `flask.request`: request received.
        `storage` -> `Storage`: storage with nodes.
    """
    targetIp = request.get_json()['ip']
    targetPort = request.get_json()['port']
    targetNodes = {}
    targetNodes.update(storage.getStorage())
    targetNodes.pop((targetIp, targetPort))
    for i in targetNodes:
        ip, port = i
        message = {
            "ip": targetIp,
            "port": targetPort,
            "payload": request.get_json()["payload"],
            "nonce": nonce,
            "hashToValiate": hashToValiate,
            "timeStamp":time(),
            "signature": request.get_json()['signature']
        }
        url = "http://" + formatUrl(ip, port) + "/validateNonce"
        print(url)
        post(url, json = message)

def informAllNodesAboutNewNode(request, storageValue):
    """ Send information about new node to all nodes in the network.

    Args:
        `request` -> `flask.request`: request received.
        `storageValue` -> `dictionary`: storage with nodes.
    """

    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    remotePublicKey = request.get_json()['publicKey']
    message =({
        "ip": remoteIp,
        "port": remotePort,
        "publicKey": remotePublicKey
    })
    
    for i in storageValue:
            ip, port = i
            url = "http://" + formatUrl(ip, port) + "/register"
            print(url)
            post(url, json = message)

def client(ip, port, privateKey, targetIp, targetPort):
    """ Function working in separate thread. Performs as client side of node. Its purpose is to inform network about new node.

    Args:
        `ip` -> `String`: host IP
        `port` -> `String`: host port
        `privateKey` -> `ecdsa.SigningKey`: host private key
        `targetIp` -> `String`: target IP of node in the network
        `targetPort` -> `String`: target port of node in the network
    """

    sleep(1)
    print("Requesting " + formatUrl(targetIp, targetPort) + " for nodes info...")
    registerMessage = {
                "ip": ip,
                "port": port,
                "publicKey": privateKey.get_verifying_key().to_string().hex()
            }
    url = "http://" + formatUrl(targetIp, targetPort) + "/new_register"
    post(url, json=registerMessage)

    # while True:                   # if 
    #     payload = input()
    #     send(targetIp, targetPort, privateKey, payload)

def signatureVerification(request, storageValue):
    """ Verifies sender signature with its publicKey in storage.

    Args:
        `request` -> `flask.request`: request received.
        `storageValue` -> `dictionary`: storage with nodes.
    """

    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    message = request.get_json()['payload']
    signature = request.get_json()['signature']
    remotePublicKey = storageValue[(remoteIp, remotePort)]
    publicKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(remotePublicKey), curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    byteSignature = bytes.fromhex(signature)
    byteMessage = bytes(str(message), 'utf-8')

    try:
        publicKey.verify(byteSignature, byteMessage)
        return True

    except:
        return False

def signatureVerificationProxy(request, storageValue):
    """ Verifies proxy sender signature with its publicKey in storage.

    Args:
        `request` -> `flask.request`: request received.
        `storageValue` -> `dictionary`: storage with nodes.
    """

    remoteIp = request.get_json()['ip']
    remotePort = request.get_json()['port']
    message = request.get_json()['payload']
    signature = request.get_json()['signature']
    remotePublicKey = storageValue[(remoteIp, remotePort)]
    publicKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(remotePublicKey), curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    byteSignature = bytes.fromhex(signature)
    byteMessage = bytes(message, 'utf-8')
    
    try:
        publicKey.verify(byteSignature, byteMessage)
        return True

    except:
        return False
def PrivKeyToFile(privateKey):
        f = open("PrivateKeys/"+str(privateKey.to_string().hex())+".txt", "wb")
        f.write(bytes(str(privateKey.to_string().hex()),'utf-8'))
        f.close()
def formatSenderAddress(request):
    """ Formats sender url address form request.

    Args:
        `request` -> `flask.request`: request received.

    Returns:
        Formatted String in form of 'IP:port' .
    """

    return "\'" + str(request.get_json()['ip']) + ":" + str(request.get_json()['port']) + "\'"

def formatUrl(ip, port):
    """ Formats url
    
    Args:
        `ip` -> `String`: ip address
        `port` -> `String`: port

    Returns:
        Formatted `String` in form of <ip>:<port>
    """

    return str(ip) + ":" + str(port)

def isSenderHost(request, ip, port):
    """ Verifies, if sender is host.

    Args:
        `request` -> `flask.request`: request received.
        `ip` -> `String`: host IP
        `port` -> `String`: host port

    Returns:
        Result of remoteIp == hostIp && remotePort == hostPort
    """
    return request.get_json()['ip'] == ip and request.get_json()['port'] == port

def readNodeSettings(argv):
    """ Reads arguments passed to script.

    Args:
        `argv` -> `sys.argv[]`: array of passed arguments to script

    Returns:
        A `tuple` of `String` values: 
            host ip,
            host port,
            remote ip,
            remote port
    """
    ip = ""
    port = ""
    remoteIp = ""
    remotePort = ""
    argHelp = "{0} -a <ip> -p <port> -r <remote_ip> -o <remote_port>".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "ha:p:r:o:", ["help", "ip", "port", "remote_ip", "remote_port"])
    except:
        print(argHelp)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(argHelp)
            sys.exit(2)
        elif opt in ("-a", "--ip"):
            ip = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-r", "--remote_ip"):
            remoteIp = arg
        elif opt in ("-o", "--remote_port"):
            remotePort = arg

    if bool(remoteIp) ^ bool(remotePort):
        print("Invalid remote input. You must fill both remoteIp and remotePort")
        print(argHelp)
        sys.exit(2)

    return ip, port, remoteIp, remotePort
