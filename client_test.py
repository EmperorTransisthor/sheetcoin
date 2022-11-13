import requests
import ecdsa
from hashlib import sha3_512
from clientUtils import send, send_all
#message generator
payload={"John sent 5SC to Anna","Daniel sent 5SC to Oscar","Andrew sent 61SC to Jason","Mark sent 45SC to Zuckerberg","Martin sent 43SC to John"}
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(bytes(payload, 'utf-8'))



#Start Nodes
import Node
message = b"Ready"
ip = "127.0.0.1"
_port = "5003"

targetIp = ip
targetPort = "5002"

node1=Node(ip,targetIp,_port,targetPort,message)
node2=Node(ip,targetIp,_port,targetPort,message)
node3=Node(ip,targetIp,_port,targetPort,message)


ip = "127.0.0.1"
port = "5004"

print("Registering!")
message = {
            "ip": "127.0.0.1",
            "port": "5002",
            "publicKey": str(publicKey.to_string().hex())
          }
requests.post("http://127.0.0.1:5001/new_register", json=message)

#input("Press enter to send message...")
#send(ip, port, privateKey, payload)

input("Press enter to send message to all...")
send_all(ip, port, privateKey, payload)

input("Press enter to show all nodes...")
requests.post("http://127.0.0.1:5001/", json=message)