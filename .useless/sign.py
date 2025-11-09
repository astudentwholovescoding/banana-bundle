from datetime import datetime
from ecdsa import SigningKey, SECP256k1
import hashlib
import json

# 1️⃣ Crée une clé privée et la clé publique correspondante
private_key = SigningKey.generate(curve=SECP256k1)
public_key = private_key.get_verifying_key()

block = {
    "timestamp": datetime.now().isoformat(),
    "sender": "Nilo"
}

message = json.dumps(block, sort_keys=True).encode()
msg_hash = hashlib.sha256(message).digest()

# 2️⃣ Signature
signature = private_key.sign(msg_hash)

print(signature)

# 3️⃣ Vérification
ok = public_key.verify(signature, msg_hash)
print("Signature valide ?", ok)
