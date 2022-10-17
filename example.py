import ecdsa
from hashlib import sha3_512

message = b"Karolinko, ty jestes cudowno kobieta"

# SECP256k1 is the Bitcoin elliptic curve
privateKey = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1, hashfunc=sha3_512)    # private key
publicKey = privateKey.get_verifying_key()                                          # public key
signature = privateKey.sign(message)
bb = publicKey.verify(signature, message)

# weryfikacja podpisu
print(type(signature))
print(type(publicKey.to_string()))
print(publicKey.verify(signature, message))

# konwersja sygnatury na stringa
print(signature)                    # sygnatura
a = signature.decode('latin-1')
print(bytes(a, 'latin-1'))          # sygnatura ponownie zakodowana (a == signature)
print(a)                            # sygnatura zdekodowana 