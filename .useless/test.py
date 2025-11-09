import datetime

from blockchain import BlockChain
from blocks import Block
from tx import Tx, MintTx
from wallets import Wallet

wallet = Wallet.from_private_key_hex('3e13d8c235f168be702392884a72c36cad089d6345af86e0397a9713fa2c4d56')

blockchain = BlockChain.load()

tx = Tx(wallet.address, 'f0f2c4faab737e938e5407471c236b39', '7c4c690b2375d476b3a941495f33aec8343778044925a3d433ad65d8e33f2518', datetime.datetime.now())

tx.sign(wallet)

blockchain.add_block(tx.to_json())

if blockchain.is_valid():
    print('ok')
    blockchain.save()