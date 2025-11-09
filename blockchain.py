import os
import json
import datetime
from ecdsa import VerifyingKey, SECP256k1

from blocks import Block
from config import *


class BlockChain:
    def __init__(self, genesis_block=None):
        if genesis_block is None:
            genesis_block = Block.generate_genesis_block()
        self.blocks = [genesis_block]

    def add_block(self, data):
        block = Block(
                self.blocks[-1].hash,
                json.dumps(data),
                datetime.datetime.now()
            )
        self.blocks.append(block)
    
    def is_valid(self):
        def add_nft(blockchain_data, address, token_id):
            if blockchain_data.get(address):
                blockchain_data[address].append(token_id)
            else:
                blockchain_data[address] = [token_id]
        def remove_nft(blockchain_data, address, token_id):
            blockchain_data.get(address).remove(token_id)

        blockchain_data = {}
        artists = {}

        for block in self.blocks:
            if block.get_hash() != block.hash:
                return False
            if block.data != 'Ø':
                block_data = json.loads(block.data)

                if block_data.get('type') == 'mint':
                    if artists.get(block_data.get('artist'), block_data.get('to')) == block_data.get('to'):
                        add_nft(blockchain_data, block_data.get('to'), block_data.get('token_id'))
                        artists[block_data.get('artist')] = block_data.get('to')
                        if len(block_data.get('data')) > 254**2:
                            return False
                    else:
                        return False

                elif block_data.get('type') == 'tx':
                    if block_data.get('token_id') in blockchain_data.get(block_data.get('from'), []):
                        add_nft(blockchain_data, block_data.get('to'), block_data.get('token_id'))
                        remove_nft(blockchain_data, block_data.get('from'), block_data.get('token_id'))
                    else:
                        return False
                    
                    public_key_bytes = bytes.fromhex(block_data.get('public_key'))
                    public_key = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
                    signature_bytes = bytes.fromhex(block_data.get('signature'))

                    if not public_key.verify(signature_bytes, json.dumps({
                        "type": 'tx',
                        "from": block_data.get('from'),
                        "to": block_data.get('to'),
                        "token_id": block_data.get('token_id'),
                        "timestamp": block_data.get('timestamp')
                    }, sort_keys=True).encode()):
                        return False
                    
        return True
    
    def save(self, filename=BLOCKCHAIN_FILE):
        if self.is_valid():
            with open(filename, 'w') as blockchain_file:
                json.dump([block.to_json() for block in self.blocks], blockchain_file, indent=2)
    
    def get_wallet_nfts(self, address):
        if not self.is_valid():
            return []
        
        owned_nfts = []

        for block in self.blocks:
            if block.data != 'Ø':
                block_data = json.loads(block.data)

                if block_data.get('to') == address:
                    owned_nfts.append(block_data.get('token_id'))
                elif block_data.get('from') == address:
                    owned_nfts.remove(block_data.get('token_id'))
        return owned_nfts
    
    def get_nft_infos(self, token_id):
        if not self.is_valid():
            return None
        
        data = None

        for block in self.blocks:
            if block.data != 'Ø':
                block_data = json.loads(block.data)

                if block_data.get('type') == 'mint' and block_data.get('token_id') == token_id:
                    data = json.loads(block_data.get('data'))
                    data['token_id'] = token_id
                    data['history'] = [block_data.get('to')]
                elif block_data.get('type') == 'tx' and block_data.get('token_id') == token_id:
                    data['history'].append(block_data.get('to'))
        return data
    
    @staticmethod
    def load(filename=BLOCKCHAIN_FILE, blockchain_json=None):
        if blockchain_json:
            blockchain = BlockChain()
            blockchain.blocks = []
            for block_json in blockchain_json:
                blockchain.blocks.append(Block.from_json(block_json))
            return blockchain
        
        if os.path.exists(filename):
            with open(filename, 'r') as blockchain_file:
                blockchain_json = json.load(blockchain_file)
            
            blockchain = BlockChain()
            blockchain.blocks = []
            for block_json in blockchain_json:
                blockchain.blocks.append(Block.from_json(block_json))

            return blockchain