
import json
from requests import post
from flask import jsonify, make_response
from time import sleep


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
    sleep(3)
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