import os
import io
import json
import base64
import datetime
import requests
from PIL import Image
from flask import Flask, render_template, session, redirect, request

from config import *
from blockchain import BlockChain
from blocks import Block
from wallets import Wallet
from tx import Tx, MintTx
from blockchainAPI import BlockchainAPI

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.jinja_env.filters['enumerate'] = enumerate

@app.route('/')
def index():
    if session.get('privateKey'):
        return redirect('/home')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    session['privateKey'] = request.form.get('privateKey')
    return redirect('/')

@app.route('/register')
def register():
    if session.get('privateKey'):
        return redirect('/home')
    new_wallet = Wallet()
    session['privateKey'] = new_wallet.private_key_hex
    return redirect('/home')

@app.route('/home')
def home():
    last_transactions = BLOCKCHAIN.blocks[-10:]
    return render_template('home.html')

@app.route('/wallet')
def wallet_route():
    if session.get('privateKey') is None:
        return redirect('/')
    wallet = Wallet.from_private_key_hex(session.get('privateKey'))

    owned_nfts = BLOCKCHAIN.get_wallet_nfts(wallet.address)
    owned_nfts = [BLOCKCHAIN.get_nft_infos(token_id) for token_id in owned_nfts]
    owned_nfts.sort(key=lambda x: x['nft_name'])

    return render_template('wallet.html', walletAddress=wallet.address, ownedNFTs=owned_nfts)

@app.route('/new-nft', methods=['GET', 'POST'])
def create_nft():
    if request.method == 'GET':
        return render_template('new_nft.html', artistName=session.get('artistName'))
    
    artist_wallet = Wallet.from_private_key_hex(session.get('privateKey'))

    qty = int(request.form.get('qty', 1))
    data_file = request.files['data']
    data = Image.open(data_file.stream)
    data = data.resize((254, 254))
    data_byte_arr = io.BytesIO()
    data.save(data_byte_arr, format='PNG')
    data_byte_arr = data_byte_arr.getvalue()
    data_base64 = base64.b64encode(data_byte_arr).decode('utf-8')

    for _ in range(qty if qty <= 50 else 50):
        new_nft = MintTx(artist_wallet.address, request.form.get('NFTName'), request.form.get('artistName'), f"data:image/png;base64,{data_base64}", datetime.datetime.now())
        BLOCKCHAIN.add_block(new_nft.to_json())
    BLOCKCHAIN.save()
    session['artistName'] = request.form.get('artistName')
    return redirect('/')

@app.route('/nft/<token_id>')
def nft(token_id):
    infos = BLOCKCHAIN.get_nft_infos(token_id)
    if session.get('privateKey'):
        wallet = Wallet.from_private_key_hex(session.get('privateKey'))
        user_address = wallet.address
    else:
        user_address = ''
    return render_template('nft.html', infos=infos, userAddress=user_address)

@app.route('/send/<token_id>', methods=['GET', 'POST'])
def send(token_id):
    global BLOCKCHAIN
    if session.get('privateKey') is None:
        return redirect('/')
    wallet = Wallet.from_private_key_hex(session.get('privateKey'))
    infos = BLOCKCHAIN.get_nft_infos(token_id)
    if infos['history'][-1] != wallet.address:
        return redirect(f'/nft/{token_id}')
    if request.method == 'GET':
        return render_template('send.html', infos=infos)
    else:
        recipient_address = request.form.get('recipientAddress', wallet.address)
        new_tx = Tx(wallet.address, recipient_address, token_id, datetime.datetime.now())
        new_tx.sign(wallet)
        BLOCKCHAIN.add_block(new_tx.to_json())
        if BLOCKCHAIN.is_valid():
            BLOCKCHAIN.save()
            return redirect(f'/nft/{token_id}')
        else:
            BLOCKCHAIN = BlockChain.load()

@app.route('/blockchain/<method>')
def blockchain(method):
    return BLOCKCHAIN_API.call(method, request)


if __name__ == '__main__':
    nodes = []

    if os.path.exists(BLOCKCHAIN_FILE):
        BLOCKCHAIN = BlockChain.load()
    else:
        node_ip = input("Please input the ip of another node to load the blockchain (empty to create another blockchain) : ")

        if node_ip:
            blockchain_page = requests.get(f'http://{node_ip}:{APP_PORT}/blockchain/getBlockchain')
            if blockchain_page.status_code == 200:
                blockchain_json = blockchain_page.json()
                BLOCKCHAIN = BlockChain.load(blockchain_json=blockchain_json)
                nodes = requests.get(f'http://{node_ip}:{APP_PORT}/blockchain/nodeList').json()
                requests.get(f'http://{node_ip}:{APP_PORT}/blockchain/nodeSubscribe')
            else:
                print('Node seems down, creating new blockchain...')
                BLOCKCHAIN = BlockChain()
        else:
            BLOCKCHAIN = BlockChain()
    
    BLOCKCHAIN.save()
    
    BLOCKCHAIN_API = BlockchainAPI()
    BLOCKCHAIN_API.nodes = nodes

    app.run(host='0.0.0.0', port=APP_PORT, debug=True)