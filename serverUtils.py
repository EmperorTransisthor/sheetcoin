import ecdsa
import sys
import getopt
from requests import post
from time import sleep
from hashlib import sha3_512
from hashlib import sha256
from time import time


PREFIX_ZEROS = '0000'

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

def proofOfWork(blockchain, listOfTransactions):
    nonce = 0
    hash_result = ''
    # difficulty from 0 to 24 bits
    # for difficulty_bits in range(24):
        # difficulty = 2 ** difficulty_bits
        # print(f'Difficulty: {difficulty} ({difficulty_bits})')

    
    print('Starting search...')
    # checkpoint the current time
    start_time = time()
    # make a new block which includes the hash from the previous block
    blockchain.createBlock(listOfTransactions, blockchain.print_previous_block()['previousHash'])

    # find a valid nonce for the new block
    (hash_result, nonce) = findHashNonce(listOfTransactions, blockchain.print_previous_block()['previousHash'], blockchain.print_previous_block()['blockIndex'])

    # checkpoint how long it took to find a result
    end_time = time()
    elapsed_time = end_time - start_time
    print('Elapsed Time: %.4f seconds' % elapsed_time)
    if elapsed_time > 0:
        # estimate the hashes per second
        hash_power = float(nonce / elapsed_time)
        print('Hashing Power: %ld hashes per second' % hash_power)

    #return results to validate in other nodes
    return nonce, hash_result

def findHashNonce(listOfTransactions, previousHash, blockIndex):
    #  here we set how long it can search nonce
    max_nonce = 2 ** 32
    for nonce in range(max_nonce):
        hash_result = sha256(str(listOfTransactions).encode('utf-8') + str(blockIndex).encode('utf-8') + str(nonce).encode('utf-8') + str(previousHash).encode('utf-8')).hexdigest()
        # check if this is a valid result, hash has to start with 4 zeros
        if hash_result.startswith(PREFIX_ZEROS): 
            print(f"Success with nonce {nonce}")
            print(f'Hash is {hash_result}')
            return (hash_result,nonce)
    print(f'Failed after {nonce} tries')
    return nonce    

def validation(nonce, hashToValidate, blockchain):
    # previous_block = blockchain.chain[0]
    previous_block = blockchain.print_previous_block()
    print(blockchain)
    # block_index = 1
    
    # while block_index < len(blockchain.chain):
    #     block = blockchain.chain[block_index]
    #     if block['previousHash'] != blockchain.hash(previous_block):
    #         return False

    #     previous_block = block
    #     block_index += 1

    #hashToValidate='{lubie placki,siemabyq}'
    #hashToValidate=sha256(hashToValidate.encode()).hexdigest()   
    if int(hashToValidate, 16) < 2 ** (256):
        return True
    return False
    
    

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
def GetTax(data):
    tax,id_trans=CheckTransaction(data)
    SaveTrans_ID(id_trans)
    return tax
def CheckTransaction(data):
    balance,payment,receiver,tax,sender,id_trans=GetDataFromJSON(data)
    if int(balance)<(int(payment)+float(tax)):
        print('ERROR! '+sender+' has not enough money!')
        return "",""
    with open("transactions.txt") as file_in:
        transactions = []
        for line in file_in:
            transactions.append(line.rstrip('\n'))
    print(transactions)
    for trans in transactions:
        if id_trans==trans:
            print('ERROR! Duplicated ID!')
            return "",""
    return tax,id_trans
def GetDataFromJSON(data):
    content=data.split('-')
    id_trans,sender,payment,receiver,tax,balance=content
    return balance,payment,receiver,tax,sender,id_trans
def SaveTrans_ID(id_trans):
    file_object = open('transactions.txt', 'a')
    file_object.write(f'{id_trans}\n')
    file_object.close()
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
