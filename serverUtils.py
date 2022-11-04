
import json
from requests import post
from flask import jsonify, make_response
from time import sleep
from hashlib import sha3_512
import ecdsa


def pushNewNodeToStorage(request, storage):
    remoteIp = request.get_json()['ip']
    remotePort = request.get_json()['port']
    remotePublicKey = request.get_json()['publicKey']
    storage.push(remoteIp, remotePort, remotePublicKey)
    print("Succesfully registered " + str(remoteIp) + ":" + str(remotePort))

def getAllNodes(storage, ip, port, publicKey):
    nodes = {}
    nodes[(ip, port)] = publicKey
    nodes.update(storage.getStorage())
    return nodes

def sendAllNodes(storage, request):
    sleep(5)
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

def informAllNodesAboutNewNode(request, storage):
    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    remotePublicKey = request.get_json()['publicKey']
    message =({
        "ip": remoteIp,
        "port": remotePort,
        "publicKey": remotePublicKey
    })
    
    for i in storage:
            ip, port = i
            url = "http://" + str(ip) + ":" + str(port) + "/register"
            print(url)
            post(url, json = message)

def send(ip, port, privateKey, payload):
    message = {
            "ip": ip,
            "port": port,
            "message": payload,
            "signature": privateKey.sign(bytes(payload, 'utf-8')).hex()
    }
    url = "http://" + str(ip) + ":" + str(port) + "/message"
    post(url, json=message)

def signatureVerification(request, storage):
    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    message = request.get_json()['message']
    signature = request.get_json()['signature']
    remotePublicKey = storage[(remoteIp, remotePort)]
    publicKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(remotePublicKey), curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    byteSignature = bytes.fromhex(signature)
    byteMessage = bytes(message, 'utf-8')
    return publicKey.verify(byteSignature, byteMessage)