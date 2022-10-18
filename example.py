import ecdsa
from hashlib import sha3_512

message = b"Template message"

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

print("\n\n")
# print(publicKey.to_string().hex())
# print(bytes.fromhex(publicKey.to_string().hex()))

# print(str(publicKey.to_string().hex()))
# print(hex(publicKey.to_string().hex()))

hex = publicKey.to_string().hex()
# print(hex)
print(signature.hex())

verka = ecdsa.VerifyingKey.from_string(bytes.fromhex(hex), curve=ecdsa.SECP256k1)

sig = bytes.fromhex(signature.hex())

print(signature)
print(sig)

print(publicKey.to_string())
print(verka.to_string())

# print(publicKey.verify(sig, message))
# print(verka.to_string() == publicKey.to_string())
# print(publicKey.verify(signature, message))
# print(verka.verify(signature, message))

# print(verka.verify(sig, message))

# print(publicKey.to_string())
# print(signature)
# print(bytes.fromhex(signature.hex()))

# print(publicKey.to_string())
# print(verka.to_string())
# print(signature)

# verka = ecdsa.VerifyingKey.from_string(hex, curve=ecdsa.SECP256k1)
# print(publicKey.to_string())
# print(verka.to_string())

msg = b"12345"
privK = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
pubK = privK.get_verifying_key().to_string().hex()

sigma = privK.sign(msg).hex()

verK = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubK), curve=ecdsa.SECP256k1)
print(verK.verify(bytes.fromhex(sigma), msg))


