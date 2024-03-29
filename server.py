import ecdsa
import sys
from storage import Storage
from hashlib import sha3_512
from flask import Flask, jsonify, request
from serverUtils import *
from Blockchain import Blockchain
from orphanBlockList import OrhpanBlockList
from threading import Thread
from subprocess import Popen
from pathlib import Path
from random import randrange
import multiprocessing
message = b"Hello World"
HELLOWORLD = "Hello World"
app = Flask(__name__)

evilnode=True
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(message)
storage = Storage()
blockchain = Blockchain()
orphanBlockList = OrhpanBlockList()

# proofOfWorkThread = Thread(target = proofOfWork, args = (blockchain))
process=None

@app.route('/', methods=['GET', 'POST'])
def index():
    """ Prints storage contents.
    """

    storage.print()
    return jsonify({"Print": True}), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Registers new node with credentials specified in request.
    """

    pushNewNodeToStorage(request, storage)
    return jsonify({'registered': True}), 200

@app.route('/new_register', methods=['GET', 'POST'])
def newRegister():
    """ Registers new node with credentials specified in request and informs all nodes in network about new node.
    """

    informAllNodesAboutNewNode(request, storage.getStorage())
    allNodes = getAllNodes(storage, _ip, _port, publicKey.to_string().hex())     # TODO(Michal Bogon): ip, port and publicKey should members of Node class
    sendAllNodes(allNodes, request)
    pushNewNodeToStorage(request, storage)
    return jsonify({'Success':'true'}), 200

@app.route('/message', methods=['GET', 'POST'])
def message():
    """ Checks sender signature and prints message if signature is valid
    """

    if signatureVerification(request, storage.getStorage()):
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['payload'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/message_all', methods=['GET', 'POST'])
def message_all():
    """ Checks sender signature, prints message if signature is valid and spreads out message to other nodes in network.
    """

    if signatureVerification(request, storage.getStorage()):
        messageAll(request, storage)
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['payload'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/receive_from', methods=['GET', 'POST'])
def receive_from():
    """ Checks proxy sender signature and prints message if signature is valid.
    """

    if signatureVerificationProxy(request, storage.getStorage()):
        print("Signature verified!")
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['payload'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200


@app.route('/mine', methods=['GET', 'POST'])
def mine():
    """ Checks sender signature, prints message if signature is valid and spreads out message to other nodes in network.
    """

    
    if signatureVerification(request, storage.getStorage()):
        print("Received transaction")
        sendMineCommandToAll(request, storage)
        receivalFailureProbability = randrange(0, 100)
        if (90 < receivalFailureProbability):
            raise Exception("\nTransaction failure P: " + str(receivalFailureProbability))
        transactionId = request.get_json()['id']
        sender = request.get_json()['sender']
        recipient = request.get_json()['receiver']
        amount = float(request.get_json()['value'])
        print("Received mining command from " + formatSenderAddress(request))
        try:
            global process
            global evilnode
            blockchain.createTransaction(transactionId, sender, recipient, amount)
            out = {'hash': '', 'nonce':0}
            queue = multiprocessing.Queue()
            queue.put(out)
            process = multiprocessing.Process(target=proofOfWork, args=(queue,blockchain, request.get_json()['payload']))
            process.start()
            process.join()
            process.terminate()
            process.join()
            copy=queue.get()
            print("Nonce acquired: " + str(copy['nonce']))
            print("Hash: " + str(copy['hash']))
            if(evilnode):
                validateToAll(request, storage, copy['nonce'], '0002ad6791f358938300bda0149f9f94919e1f3560e33c6317c9e7aa37932883')
            validateToAll(request, storage, copy['nonce'], copy['hash'])
            return jsonify({'verifiedSignature': True}), 200
            
        except Exception as e:
            if str(e) == "Insufficient funds":
                return jsonify({'verifiedSignature': True, 'transactionValid': False}), 401
            elif str(e) == "Duplicate transaction":
                print("Duplicate transaction: " + str(transactionId))
                return jsonify({'verifiedSignature': True, 'transactionValid': False}), 402 
            else:
                print("Caught error:")
                print(e)
                return jsonify({'verifiedSignature': True}), 500
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/receive_mine', methods=['GET', 'POST'])
def receive_mine():
    """ Start mining
    """

    if signatureVerification(request, storage.getStorage()):
        print("Received mining command from " + formatSenderAddress(request))
        receivalFailureProbability = randrange(0, 100)
        if (90 < receivalFailureProbability):
            raise Exception("\nTransaction failure P: " + str(receivalFailureProbability))
        global process
        out = {'hash': '', 'nonce':0}
        queue = multiprocessing.Queue()
        queue.put(out)
        process = multiprocessing.Process(target=proofOfWork, args=(queue,blockchain, request.get_json()['payload']))
        process.start()
        process.join()
        process.terminate()
        process.join()
        copy=queue.get()
        print("Nonce acquired: " + str(copy['nonce']))
        print("Hash: " + str(copy['hash']))
        validateToAll(request, storage, copy['nonce'], copy['hash'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/validateNonce', methods=['GET', 'POST'])
def validateNounce():
    """ Checks if Nounce is working if yes then it sends true else false
    """

    receivalFailureProbability = randrange(0, 100)
    if(90<receivalFailureProbability):
        raise Exception("\nMine connection failure P: " + str(receivalFailureProbability))
    if signatureVerification(request, storage.getStorage()):
    # if signatureVerification(request, storage.getStorage()):
        # sendMineCommandToAll(request, storage)
        
        print("Connection successful")
        validatedHash = request.get_json()['hashToValiate']
        nonce = request.get_json()['nonce']
        print("Received validation command from " + formatSenderAddress(request))
        print("Hash to validate: " + validatedHash)
        currtimestamp=request.get_json()['timeStamp']
        print('HEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
        if(validation(nonce, validatedHash, blockchain,currtimestamp)):
            print("Hash is correct")
            blockchain.print()
            blockchain.createBlock(validatedHash, nonce)
            blockchain.print()
        else:
            print("Orphan block detected, pushing into orphan blocks!")
            orphanBlockList.push(validatedHash)
            orphanBlockList.print()
        # print("Data: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200

    else:
        print("\n\nConnection failure!\n\n")
    
    return jsonify({'verifiedSignature': False}), 200

if __name__ == '__main__':
    with app.app_context():
        _ip, _port, targetIp, targetPort = readNodeSettings(sys.argv)
        print("Starting node on " + formatUrl(_ip, _port))

        # TODO(EmperorTransisthor): currently commented out, because console is not working
        PrivKeyToFile(privateKey)
        # pyScript = "x-terminal-emulator -e " + "python3 " + str(Path().resolve()) + "/console.py -a " + str(_ip) + " -p " + str(_port) + " -s " + str(privateKey.to_string().hex())
        # Popen(pyScript, shell=True)

        if targetIp and targetPort:
            thread1 = Thread(target = client, args = (_ip, _port, privateKey, targetIp, targetPort))
            thread1.start()
        
    app.run(host=_ip, port=_port)
