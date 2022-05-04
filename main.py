from typing import List
from flask import Flask, request
from blockchain import Blockchain
from flask import Flask
import json

app = Flask("app name")
chain = Blockchain()
users: List[dict] = []


@app.route("/")
def homepage():
    return f'we have {len(chain.chain)} blocks now.'


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_dict = {"length": len(chain.chain), "chain": chain.chain}
    return json.dumps(chain_dict, default=lambda obj: obj.__dict__)


@app.route('/unmined_blocks', methods=['GET'])
def get_unmined_blocks():
    chain_dict = {"unmined blocks": chain.unmined_chain}

    return json.dumps(chain_dict, default=lambda obj: obj.__dict__)


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ['sender', 'amount', 'recipient']
    for field in required_fields:
        if not tx_data.get(field):
            return {"result": "Invalid transaction data"}, 400

    sender = tx_data['sender']
    amount = tx_data['amount']
    recipient = tx_data['recipient']

    transaction = f'{sender}, {amount}, {recipient}'
    chain.add_transaction(transaction)
    return {"result": "Transaction added successfully"}, 200


@app.route('/mine', methods=['GET'])
def mine():
    if not chain.unmined_chain:
        return {'result': 'No unmined_blocks found'}, 200

    block_added = chain.mine()
    return {'result': block_added}, 200


@app.route('/create_user', methods=['POST'])
def create_user():
    user_data = request.get_json()
    required_fields = ['username', 'password']
    for field in required_fields:
        if not user_data.get(field):
            return {"result": "Invalid user data"}, 400

    username = user_data['username']
    password = user_data['password']

    for u in users:
        if u['username'] == username:
            return {"result": "User already exists"}, 400

    user = {'username': username, 'password': password}
    users.append(user)
    return {"result": "User registered successfully"}, 200


@app.route('/login', methods=['POST'])
def login():
    user_data = request.get_json()
    required_fields = ['username', 'password']
    for field in required_fields:
        if not user_data.get(field):
            return {"result": "Invalid user data"}, 400

    username = user_data['username']
    password = user_data['password']

    for user in users:
        if user['username'] == username and user[
                'password'] == password:
            return {"result": "User logged in successfully"}, 200

    return {"result": "Invalid username or password"}, 400


chain.add_transaction("tx1")
chain.mine()
chain.show()

chain.add_transaction("tx2")
chain.mine()
chain.show()

app.run(host="0.0.0.0", port=8000)
