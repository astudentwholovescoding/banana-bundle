import json

from config import ENV

class BlockchainAPI:
    def __init__(self):
        self.methods = {
            "getBlockchain": self.get_blockchain,
            "getLength": self.get_length,
            "getBlock": self.get_block
        }
    
    def call(self, method, args):
        return self.methods.get(method, lambda args: "Unknown method")(args)
    
    def get_blockchain(self, args):
        with open(ENV['BLOCKCHAIN_FILE']) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return json.dumps(blockchain)
    
    def get_length(self, args):
        with open(ENV['BLOCKCHAIN_FILE']) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return str(len(blockchain))
    
    def get_block(self, args):
        block_id = int(args.get('id', '-1'))
        with open(ENV['BLOCKCHAIN_FILE']) as blockchain_file:
            blockchain = json.load(blockchain_file)
        return json.dumps(blockchain[block_id])