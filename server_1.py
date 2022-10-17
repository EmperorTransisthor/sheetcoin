import ecdsa
import requests
from storage import Storage
from hashlib import sha3_512
from flask import Flask, jsonify, request
from json import dumps

message = b"Hello World"
HELLOWORLD = message
app = Flask(__name__)

ip = "127.0.0.1"
_port = "5001"

privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(message)
storage = Storage()

@app.route('/', methods=['GET', 'POST'])
def index():
    jsonMessage = jsonify({'message' : message.decode('latin-1'),
                           'signature' : signature.decode('latin-1')})
    if (request.method == 'POST' and request.get_json()['connect']): # and request.form['connect']
        print("Connection from " + str(request.remote_addr))
        remoteIp = request.remote_addr
        remotePort = request.get_json()['port']
        remotePublicKey = request.get_json()['publicKey']
        storage.push(remoteIp, remotePort, remotePublicKey)
        some_json = request.get_json()
        print("Sucess? : ")
        storage.print()
        return jsonify({'you sent' : some_json}), 201
    # elif (request.method == 'GET'):
    #     # some_json = request.get_json()
    #     return jsonMessage, 201
    else:
        return jsonify({"about": HELLOWORLD}), 202

@app.route('/register', methods=['GET', 'POST'])
def register():
    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    remotePublicKey = request.get_json()['publicKey']
    storage.push(remoteIp, remotePort, remotePublicKey)
    print("Succesfully registered " + str(remoteIp) + ":" + str(remotePort))
    return jsonify({'registered': True}), 200

if __name__ == '__main__':
    with app.app_context():
        message = {
            "connect": True,
            "port": "5005",
            "publicKey": publicKey.to_string().hex()
        }
        requests.post("http://127.0.0.1:5002/", json=message)
        
    app.run(host=ip, port=_port)
