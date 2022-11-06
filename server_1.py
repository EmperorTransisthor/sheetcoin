import ecdsa
import requests
from threading import Thread
from storage import Storage
from hashlib import sha3_512
from node import Node
from flask import Flask, jsonify, request
from serverUtils import *

message = b"Hello World"
HELLOWORLD = "Hello World"
app = Flask(__name__)

ip = "127.0.0.1"
_port = "5001"

privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(message)
storage = Storage()

@app.route('/', methods=['GET', 'POST'])
def index():
    print("Connection from " + str(request.remote_addr))
    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    remotePublicKey = request.get_json()['publicKey']
    storage.push(remoteIp, remotePort, remotePublicKey)
    print("Sucess? : ")
    storage.print()
    return jsonify({'you sent' : HELLOWORLD}), 201

@app.route('/register', methods=['GET', 'POST'])
def register():
    pushNewNodeToStorage(request, storage)
    return jsonify({'registered': True}), 200

@app.route('/new_register', methods=['GET', 'POST'])
def newRegister():        
    informAllNodesAboutNewNode(request, storage.getStorage())
    allNodes = getAllNodes(storage, ip, _port, publicKey.to_string().hex())     # TODO(Michal Bogon): ip, port and publicKey should members of Node class
    sendAllNodes(allNodes, request)
    pushNewNodeToStorage(request, storage)
    return jsonify({'Success':'true'}), 200

@app.route('/message', methods=['GET', 'POST'])
def message():
    if signatureVerification(request, storage.getStorage()):
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/message_all', methods=['GET', 'POST'])
def message_all():
    if signatureVerification(request, storage.getStorage()):
        messageAll(request, storage)
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

@app.route('/receive_from', methods=['GET', 'POST'])
def receive_from():
    if signatureVerificationProxy(request, storage.getStorage()):
        print("Signature verified!")
        print("Received message from " + formatSenderAddress(request))
        print("Message: " + request.get_json()['message'])
        return jsonify({'verifiedSignature': True}), 200
    
    return jsonify({'verifiedSignature': False}), 200

if __name__ == '__main__':
    # with app.app_context():
    #     thread1 = Thread(target = client, args = (ip, _port, privateKey))
    #     thread1.start()
        
    app.run(host=ip, port=_port)
