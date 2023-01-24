import requests
import ecdsa
from hashlib import sha3_512
from clientUtils import send, send_all
from clientUtils import mine
#message generator
payload1="146ae5b084f930ea54fae5b171d87cb9-John-5-Andrew"#id,sender,value,receiver,tax,sender_balance
payload2="2a175d779041fc9588e8d5a793301824-Andrew-260-Mark"
payload3="9354aa7d41de92df316845bee0d1e316-Andrew-321-John"
payload4="5c2351993d8e607e5e3ddb6eeacb2079-Juliette-5-Steven"#oopsie, no money!

privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(bytes(str(payload1), 'utf-8'))

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
send(ip, port, privateKey, str(payload1))

input("Press enter to send message to all...")
send_all(ip, port, privateKey, str(payload1))

input("Press enter to show all nodes...")
requests.post("http://127.0.0.1:5001/", json=message)
input("Press enter to mine...")
mine(ip, port, privateKey, str(payload1))
input("Press enter to mine...")
mine(ip, port, privateKey, str(payload2))
input("Press enter to mine...")
mine(ip, port, privateKey, str(payload3))
print("CHEATMODE ACTIVATED! Try to pay more than you've got!")
input("Press enter to mine...")
mine(ip, port, privateKey, str(payload4))
print("Oopsie! I've duplicated first transaction...")
input("Press enter to mine...")
mine(ip, port, privateKey, str(payload1))
