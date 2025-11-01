import json
import hashlib

class Tx:
    def __init__(self, from_, to, token_id, timestamp):
        self.from_ = from_
        self.to = to
        self.token_id = token_id,
        self.timestamp = timestamp
    
    def sign(self, wallet):
        self.signature = wallet.private_key.sign(json.dumps({
            "type": 'tx',
            "from": self.from_,
            "to": self.to,
            "token_id": self.token_id[0],
            "timestamp": self.timestamp.isoformat()
        }, sort_keys=True).encode()).hex()
        self.public_key = wallet.public_key_hex
    
    def to_json(self):
        return {
            "type": 'tx',
            "from": self.from_,
            "to": self.to,
            "token_id": self.token_id[0],
            "timestamp": self.timestamp.isoformat(),
            "signature": self.signature,
            "public_key": self.public_key
        }

class MintTx:
    def __init__(self, artist_address, nft_name, artist, nft, timestamp):
        data = json.dumps({
            "nft_name": nft_name,
            "artist": artist,
            "data": nft
        })

        token_id = hashlib.sha256((artist_address+data+str(timestamp)).encode()).hexdigest()

        self.artist_address = artist_address
        self.data = data
        self.token_id = token_id
        self.timestamp = timestamp
    
    def to_json(self):
        return {
            "type": 'mint',
            "from": 'Nil0',
            "to": self.artist_address,
            "token_id": self.token_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }