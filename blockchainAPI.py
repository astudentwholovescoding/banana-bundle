import json
import requests

from config import ENV

class BlockchainAPI:
    def __init__(self):
        self.methods = {
            "ping": self.ping,
            "nodeSubscribe": self.node_subscribe,
            "nodeList": self.node_list,
            "getBlockchain": self.get_blockchain,
            "getLength": self.get_length,
            "getBlock": self.get_block
        }
        self.nodes = []
    
    def call(self, method, request):
        return self.methods.get(method, lambda args: "Unknown method")(request)
    
    def ping(seld, request):
        return 'Service up'

    def node_subscribe(self, request):
        if requests.get(f'http://{request.remote_addr}:{ENV['APP_PORT']}/blockchain/ping').status_code == 200:
            if request.remote_addr == request.host.split(':')[0]:
                return "A node can't subscribe to himself"
            self.nodes.append(request.remote_addr)
            return 'Node subscribed'
        else:
            return "You aren't a node"

    def node_list(self, request):
        return json.dumps(self.nodes)

    def get_blockchain(self, request):
        with open(ENV['BLOCKCHAIN_FILE']) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return json.dumps(blockchain)
    
    def get_length(self, request):
        with open(ENV['BLOCKCHAIN_FILE']) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return str(len(blockchain))
    
    def get_block(self, request):
        block_id = int(request.args.get('id', '-1'))
        with open(ENV['BLOCKCHAIN_FILE']) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return json.dumps(blockchain[block_id])