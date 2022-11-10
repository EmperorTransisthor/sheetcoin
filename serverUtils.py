import ecdsa
import sys
import getopt
from requests import post
from time import sleep
from hashlib import sha3_512


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
            "message": request.get_json()['message'],
            "signature": request.get_json()['signature']
        }
        url = "http://" + formatUrl(ip, port) + "/receive_from"
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
    message = request.get_json()['message']
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

def signatureVerificationProxy(request, storageValue):
    """ Verifies proxy sender signature with its publicKey in storage.

    Args:
        `request` -> `flask.request`: request received.
        `storageValue` -> `dictionary`: storage with nodes.
    """

    remoteIp = request.get_json()['ip']
    remotePort = request.get_json()['port']
    message = request.get_json()['message']
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

    if remoteIp ^ remotePort:
        print("Invalid remote input. You must fill both remoteIp and remotePort")
        print(argHelp)
        sys.exit(2)

    return ip, port, remoteIp, remotePort
