import json
import ecdsa
from flask import Flask, jsonify, request
from hashlib import sha3_512

HELLOWORLD = b"Karolinko, ty jestes cudowno kobieta!"
message = HELLOWORLD
aes_key = HELLOWORLD # temp TODO: Marcin Wojtowicz

app = Flask(__name__)


# zaszyfrowanie klucza prywatnego i wczytywanie go z pliku wraz z odszyfrowaniem (klucz AES znajduje się w serwerze/hardcode)
# 
# with.open BLABLA (TODO: Marcin Wojtowicz)
#
# 
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key #temp
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