from requests import post

def send(ip, port, privateKey, payload):
    """ Sends message to specified node.

    Args:
        `ip` -> `String`: target IP
        `port` -> `String`: target port
        `privateKey` -> `ecdsa.SigningKey`: host private key
        `payload` -> `String`: content of the message
    """

    message = {
            "ip": ip,
            "port": port,
            "payload": payload,
            "signature": privateKey.sign(bytes(payload, 'utf-8')).hex()
    }
    url = "http://" + str(ip) + ":" + str(port) + "/message"
    post(url, json=message)

def send_all(ip, port, privateKey, payload):
    """ Sends message to specified node and orders it to send message to whole network.

    Args:
        `ip` -> `String`: target IP
        `port` -> `String`: target port
        `privateKey` -> `ecdsa.SigningKey`: host private key
        `payload` -> `String`: content of the message
    """

    message = {
            "ip": ip,
            "port": port,
            "payload": payload,
            "signature": privateKey.sign(bytes(payload, 'utf-8')).hex()
    }
    url = "http://" + str(ip) + ":" + str(port) + "/message_all"
    response = post(url, json=message)
    # print(response.content.decode('utf-8'))

def mine(ip, port, privateKey, payload):
    """ Sends mine command to specified node and orders it to send mine command to whole network.
    After mining is done prints added block.

    Args:
        `ip` -> `String`: target IP
        `port` -> `String`: target port
        `privateKey` -> `ecdsa.SigningKey`: host private key
        `payload` -> `String`: content of the message
    """

    message = {
            "ip": ip,
            "port": port,
            "payload": payload,
            "signature": privateKey.sign(bytes(payload, 'utf-8')).hex()
    }
    url = "http://" + str(ip) + ":" + str(port) + "/mine"
    post(url, json=message)

