
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
    # for i in storage, send payload to all + endpoint receive_from
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
            "message": request.get_json()['message'],
            "signature": request.get_json()['signature']
        }
        url = "http://" + str(ip) + ":" + str(port) + "/receive_from"
        print(url)
        post(url, json = message)

def informAllNodesAboutNewNode(request, storageValue):
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

def send_all(ip, port, privateKey, payload):
    message = {
            "ip": ip,
            "port": port,
            "message": payload,
            "signature": privateKey.sign(bytes(payload, 'utf-8')).hex()
    }
    url = "http://" + str(ip) + ":" + str(port) + "/message_all"
    response = post(url, json=message)
    # print(response.content.decode('utf-8'))

def client(ip, port, privateKey, targetIp, targetPort):
    sleep(1)
    registerMessage = {
                "ip": ip,
                "port": port,
                "publicKey": privateKey.get_verifying_key().to_string().hex()
            }
    url = "http://" + str(targetIp) + ":" + str(targetPort) + "/new_register"
    post(url, json=registerMessage)

    # while True:                   # if 
    #     payload = input()
    #     send(targetIp, targetPort, privateKey, payload)


def signatureVerification(request, storageValue):
    remoteIp = request.remote_addr
    remotePort = request.get_json()['port']
    message = request.get_json()['message']
    signature = request.get_json()['signature']
    remotePublicKey = storageValue[(remoteIp, remotePort)]
    publicKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(remotePublicKey), curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    byteSignature = bytes.fromhex(signature)
    byteMessage = bytes(message, 'utf-8')
    return publicKey.verify(byteSignature, byteMessage)

def signatureVerificationProxy(request, storageValue):
    remoteIp = request.get_json()['ip']
    remotePort = request.get_json()['port']
    message = request.get_json()['message']
    signature = request.get_json()['signature']
    remotePublicKey = storageValue[(remoteIp, remotePort)]
    publicKey = ecdsa.VerifyingKey.from_string(bytes.fromhex(remotePublicKey), curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    byteSignature = bytes.fromhex(signature)
    byteMessage = bytes(message, 'utf-8')
    return publicKey.verify(byteSignature, byteMessage)

def formatSenderAddress(request):
    return "\'" + str(request.get_json()['ip']) + ":" + str(request.get_json()['port'])

def isSenderHost(request, ip, port):
    return request.get_json()['ip'] == ip and request.get_json()['port'] == port
