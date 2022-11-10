import ecdsa
import sys
from threading import Thread
from storage import Storage
from hashlib import sha3_512
from node import Node
from flask import Flask, jsonify, request
from serverUtils import *

message = b"Hello World"
HELLOWORLD = "Hello World"
app = Flask(__name__)

privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(message)
storage = Storage()


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
        print("Message: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/message_all', methods=['GET', 'POST'])
def message_all():
    """ Checks sender signature, prints message if signature is valid and spreads out message to other nodes in network.
    """

    if signatureVerification(request, storage.getStorage()):
        messageAll(request, storage)
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/receive_from', methods=['GET', 'POST'])
def receive_from():
    """ Checks proxy sender signature and prints message if signature is valid.
    """

    if signatureVerificationProxy(request, storage.getStorage()):
        print("Signature verified!")
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

if __name__ == '__main__':
    with app.app_context():
        _ip, _port, targetIp, targetPort = readNodeSettings(sys.argv)
        print("Starting node on " + formatUrl(_ip, _port))

        if targetIp and targetPort:
            thread1 = Thread(target = client, args = (_ip, _port, privateKey, targetIp, targetPort))
            thread1.start()
        
    app.run(host=_ip, port=_port)
