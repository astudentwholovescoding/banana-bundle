import json
import requests
import datetime

from config import *
from blockchain import BlockChain

class BlockchainAPI:
    def __init__(self):
        self.methods = {
            "ping": self.ping,
            "nodeSubscribe": self.node_subscribe,
            "nodeList": self.node_list,
            "getBlockchain": self.get_blockchain,
            "getLength": self.get_length,
            "getBlock": self.get_block,
            "addBlock": self.add_block
        }
        self.nodes = []
    
    def call(self, method, request):
        return self.methods.get(method, lambda args: "Unknown method")(request)
    
    def ping(seld, request):
        return 'Service up'

    def node_subscribe(self, request):
        if request.remote_addr == request.host.split(':')[0]:
            return "A node can't subscribe to himself"
        self.nodes.append(request.remote_addr)
        return 'Node subscribed'

    def node_list(self, request):
        return json.dumps(self.nodes)

    def get_blockchain(self, request):
        with open(BLOCKCHAIN_FILE) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return json.dumps(blockchain)
    
    def get_length(self, request):
        BLOCKCHAIN = BlockChain.load()
        return str(len(BLOCKCHAIN.blocks))
    
    def get_block(self, request):
        block_id = int(request.args.get('id', '-1'))
        BLOCKCHAIN = BlockChain.load()
        return json.dumps(BLOCKCHAIN.blocks[block_id].to_json())
    
    def add_block(self, request):
        BLOCKCHAIN = BlockChain.load()

        previous_block_hash = request.args.get('previousBlockHash')
        data = request.args.get('data')
        timestamp = datetime.datetime.fromisoformat(request.args.get('timestamp'))
        hash = request.args.get('hash')

        if BLOCKCHAIN.blocks[-1]['hash'] == previous_block_hash:
            BLOCKCHAIN.add_block(data, timestamp)
            if BLOCKCHAIN.blocks[-1].get_hash() == hash and BLOCKCHAIN.is_valid:
                BLOCKCHAIN.save()
                return "Block added successfully"
        return "Something happens"