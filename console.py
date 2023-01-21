import requests
import sys
import getopt
import argparse
import ecdsa
from hashlib import sha3_512
import traceback

def send_request(command, payload):
    url = "http://" + ip + ":" + port + "/" + command
    response = ""
    try:
        response = requests.post(url, payload)
        print(response.text)
    except requests.exceptions.InvalidSchema:
        print("No connection adapters were found for \'" + str(url) + "\'")
    except Exception:
        print(traceback.format_exc())

ip = ""
port = ""
privateKey = ""

try:
    opts, _ = getopt.getopt(sys.argv[1:], "a:p:s:", ["ip", "port", "sig"])
except:
    print("error code 1")
    sys.exit(1)

for opt, arg in opts:
    if opt in ("-a", "--ip"):
        ip = arg
    elif opt in ("-p", "--port"):
        port = arg
    elif opt in ("-s", "--sig"):
        privateKey = arg
        privateKey = ecdsa.SigningKey.from_string(bytes.fromhex(privateKey), curve=ecdsa.SECP256k1, hashfunc=sha3_512)
    else:
        print("error code 2")
        sys.exit(2)

if ip == "":
    print("Missing ip")
    sys.exit(3)
elif port == "":
    print("Missing port")
    sys.exit(3)
elif privateKey == "":
    print("Missing privateKey")
    sys.exit(3)

print("Console of " + ip + ":" + port + " server")

while True:
    cmd = input("NODE> ")
    if cmd == "send":
        try:
            remoteIp = input("ip: ")
            remotePort = input("port: ")
            message = input("message: ")
            payload = {
                "ip": str(remoteIp),
                "port": str(remotePort),
                "message": str(message),
                "signature": str(privateKey.sign(bytes(message, 'utf-8')))
            }
            send_request("message", payload)
        except Exception:
            print(traceback.format_exc())
    elif cmd == "exit" or "q":
        sys.exit(0)
    else:
        print("Unknown command. Commands:")
        print("     send")
        print("     exit | q")

    
