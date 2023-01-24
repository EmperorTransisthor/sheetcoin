import ecdsa
import sys
from concurrent.futures import ThreadPoolExecutor
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

message = b"Hello World"
HELLOWORLD = "Hello World"
app = Flask(__name__)

privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(message)
storage = Storage()
blockchain = Blockchain()
orphanBlockList = OrhpanBlockList()

# proofOfWorkThread = Thread(target = proofOfWork, args = (blockchain))
executor = ThreadPoolExecutor(1)

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
        sendMineCommandToAll(request, storage)
        print("Received mining command from " + formatSenderAddress(request))
        # print("Data: " + str(request.get_json()['payload']))
        # start proof_of work - serching for candidate block
        future = executor.submit(proofOfWork, blockchain, request.get_json()['payload'],)
        resultNonce, resultHash = future.result()
        print("Nonce acquired: " + str(resultNonce))
        print("Hash: " + str(resultHash))
        validateToAll(request, storage, resultNonce, resultHash)
        tax=GetTax(request.get_json()['payload'])
        print("Got "+str(tax)+"SC fee!")
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/receive_mine', methods=['GET', 'POST'])
def receive_mine():
    """ Start mining
    """

    if signatureVerification(request, storage.getStorage()):
        print("Received mining command from " + formatSenderAddress(request))
        future = executor.submit(proofOfWork, blockchain, request.get_json()['payload'],)
        resultNonce, resultHash = future.result()
        print("Nonce acquired: " + str(resultNonce))
        print("Hash: " + str(resultHash))
        validateToAll(request, storage, resultNonce, resultHash)
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/validateNonce', methods=['GET', 'POST'])
def validateNounce():
    """ Checks if Nounce is working if yes then it sends true else false
    """

    receivalFailureProbability = randrange(0, 100)
    print("\nFailue: " + str(receivalFailureProbability))
    if signatureVerification(request, storage.getStorage()) and (90 > receivalFailureProbability):
        # sendMineCommandToAll(request, storage)
        validatedHash = request.get_json()['hashToValiate']

        print("Received validation command from " + formatSenderAddress(request))
        print("Hash to validate: " + validatedHash)
        if(validation(request.get_json()['nonce'], validatedHash, blockchain)):
            print("Hash is correct")
            print("Blockchain: "+str(blockchain))
            executor.shutdown()
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
        pyScript = "x-terminal-emulator -e " + "python3 " + str(Path().resolve()) + "/console.py -a " + str(_ip) + " -p " + str(_port) + " -s " + str(privateKey.to_string().hex())
        Popen(pyScript, shell=True)

        if targetIp and targetPort:
            thread1 = Thread(target = client, args = (_ip, _port, privateKey, targetIp, targetPort))
            thread1.start()
        
    app.run(host=_ip, port=_port)
