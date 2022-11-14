import requests
import ecdsa
from hashlib import sha3_512
from clientUtils import send, send_all
from Blockchain import Blockchain
from clientUtils import mine
#message generator
payload={"John sent 5SC to Anna","Daniel sent 5SC to Oscar","Andrew sent 61SC to Jason","Mark sent 45SC to Zuckerberg","Martin sent 43SC to John"}
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(bytes(str(payload), 'utf-8'))

blockchain = Blockchain()

ip = "127.0.0.1"
port = "5001"

print("Registering!")
message = {
            "ip": "127.0.0.1",
            "port": "5001",
            "publicKey": str(publicKey.to_string().hex())
          }
requests.post("http://127.0.0.1:5001/new_register", json=message)

input("Press enter to send message...")
send(ip, port, privateKey, str(payload))

input("Press enter to send message to all...")
send_all(ip, port, privateKey, str(payload))

input("Press enter to show all nodes...")
requests.post("http://127.0.0.1:5001/", json=message)

input("Press enter to mine...")
mine(ip, port, privateKey, str(payload))