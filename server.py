import json
import hashlib
import base64
import ecdsa
from flask import Flask, jsonify, request
from hashlib import sha3_512
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode
from base64 import b64decode

class AESCrypto(object):

    def __init__(self, aes_key): 
        self.aes_key = hashlib.sha256(aes_key ).digest()

    def encrypt(self, str_to_encrypt): #private key encryption
        str_to_encrypt_padded = str_to_encrypt + (AES.block_size - len(str_to_encrypt) % AES.block_size) * chr(AES.block_size - len(str_to_encrypt) % AES.block_size)
        iv = Random.new().read(AES.block_size)
        str_encrypted = AES.new(self.aes_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + str_encrypted.encrypt(str_to_encrypt.encode()))

    def decrypt(self, str_to_decrypt):  #private key decryption
        str_to_decrypt = base64.b64decode(str_to_decrypt)
        iv = str_to_decrypt[:AES.block_size]
        str_encrypted = AES.new(self.aes_key, AES.MODE_CBC, iv)
        to_depad=str_encrypted.decrypt(str_to_decrypt[AES.block_size:])
        str_depaded=to_depad[:-ord(to_depad[len(to_depad)-1:])]
        return str_depaded.decode('utf-8')


HELLOWORLD = b"Karolinko, ty jestes cudowno kobieta!"
message = HELLOWORLD
#aes_key=HELLOWORLD

aes_key = b'\xcd\xd8\xce?\xa0\x81\x11\xa8F\xf6\x14,\xce\x9d@S'
app = Flask(__name__)


instance=AESCrypto(aes_key)
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
#privKEY_save, nonce, mac = encryptor(privateKey,aes_key)
privateKey_to_save=instance.encrypt(str(privateKey))

f = open("pubk.txt", "wb")  #Saving To File
f.write(privateKey_to_save)
f.close()

#f = open("pubk.txt", "rb")
#privKEYdecoded=f.read()
#f.close()
#privateKey2 = decryptor(privKEYdecoded, nonce, mac, aes_key)
#privateKey2=instance.decrypt(privKEYdecoded)



publicKey = privateKey.get_verifying_key()                                          # public key
publicKeyString = publicKey.to_string()

signature = privateKey.sign(message)
# bb = publicKey.verify(signature, message)

@app.route('/', methods=['GET', 'POST'])
def index():
    jsonMessage = jsonify({'message' : message.decode('latin-1'),
                           'signature' : signature.decode('latin-1')})
    if (request.method == 'POST'):
        some_json = request.get_json()
        return jsonify({'you sent' : some_json}), 201
    elif (request.method == 'GET'):
        # some_json = request.get_json()
        return jsonMessage, 201
    else:
        return jsonify({"about": HELLOWORLD}), 202


if __name__ == '__main__':
    app.run(debug=True)



    