import os
import json
import hashlib
import datetime

class Block:
    def __init__(self, previous_block_hash, data, timestamp, hash=None):
        self.previous_block_hash = previous_block_hash
        self.data = data
        self.timestamp = timestamp
        if hash is not None:
            self.hash = hash
        else:
            self.hash = self.get_hash()
    
    @staticmethod
    def generate_genesis_block():
        return Block('Ø', 'Ø', datetime.datetime.now())

    def get_hash(self):
        header = (
            str(self.previous_block_hash) +
            str(self.data) +
            str(self.timestamp)
        ).encode()

        inner_hash = hashlib.sha256(header).hexdigest().encode()
        outer_hash = hashlib.sha256(inner_hash).hexdigest()

        return outer_hash

    def to_json(self):
        return {
                "previous_block_hash": self.previous_block_hash,
                "data": self.data,
                "timestamp": self.timestamp.isoformat(),
                "hash": self.hash
            }
    
    @staticmethod
    def from_json(block_json):
        return Block(
            previous_block_hash=block_json.get('previous_block_hash'),
            data=block_json.get('data'),
            timestamp=datetime.datetime.fromisoformat(block_json.get('timestamp')),
            hash=block_json.get('hash')
        )