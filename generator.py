import ecdsa
import json
from flask import Flask, jsonify, request
from hashlib import sha3_512
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

class Generator:
    def getPrivateKey():
        return ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)

    def savePrivateKey(privateKey):
        f = open("pubk.txt", "wb")
        f.write(privateKey)
        f.close()

    def loadPrivateKey():
        f = open("pubk.txt", "r")
        privateKey=f.read()
        f.close()
        return privateKey

    def encryptor(base_str, AESkey):
        BYTEstr = json.dumps(str(base_str)).encode()
        NONCE = Random.get_random_bytes(AES.block_size-1)
        cipher = AES.new(AESkey,AES.MODE_OCB,NONCE)
        ciphertxt, MAC = cipher.encrypt_and_digest(BYTEstr)
        return b64encode(ciphertxt).decode(),NONCE.decode('latin-1'),MAC.decode('latin-1')
    
    def decryptor(base_str, NONCE, MAC, AESkey):
        ciphertxt=b64decode(base_str)
        cipher=AES.new(AESkey,AES.MODE_OCB,NONCE.encode('latin-1'))
        out_str=cipher.decrypt_and_verify(ciphertxt,MAC.encode('latin-1')).decode()
        return json.loads(json.loads(out_str))
