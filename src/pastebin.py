from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# 1. Generate a private key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

print(private_key.private_numbers().p)
print(private_key.private_numbers().q)
print(private_key.private_numbers().d)

# 2. Generate the public key from the private key
public_key = private_key.public_key()
print(public_key.public_numbers())

# Data to be signed (in a JWT, this would be the header + payload)
data = b"example data to sign"

# 3. Sign the data using the private key
signature = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())
signature_int = int.from_bytes(signature, byteorder="big")
# print(signature_int)

# print("Signature:", signature)


try:
    public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
    print("Signature is valid!")
except Exception as e:
    print("Signature is invalid:", e)
