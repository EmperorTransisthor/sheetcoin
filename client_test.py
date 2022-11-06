import requests
import ecdsa
from hashlib import sha3_512
from serverUtils import send, send_all

payload = "Hello World"
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(bytes(payload, 'utf-8'))

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
send(ip, port, privateKey, payload)

input("Press enter to semd message to all...")
send_all(ip, port, privateKey, payload)
