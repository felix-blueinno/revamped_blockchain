import json
from flask import Flask, request
from block import Block
from blockchain import Blockchain
from typing import List
from constants import USER_DATA_DIR
from user import User
from nodes import Nodes
import requests


class FlaskServer:
    def __init__(self, chain: Blockchain,
                 users: List[User],
                 server_name: str = "app",
                 port: int = 8000,):
        self.chain = chain
        self.users = users
        self.nodes = Nodes()

        self.server_name = server_name
        self.port = port

    def run(self):
        app = Flask("app name")

        @app.route("/")
        def homepage():
            self.nodes.root_url = request.url_root
            self.nodes.knock_peers()

            self.consensus()

            return f'we have {len(self.chain.chain)} blocks now.'

        @app.route('/peers', methods=['GET'])
        def get_peers():
            return {"peers": list(self.nodes.peers)}

        @app.route('/register_node', methods=['POST'])
        def register_node():

            if not request.get_json().get('node_address'):
                return {"result": "Failed. Missing node address"}, 400

            node_address = request.get_json()['node_address']
            self.nodes.add_node(node_address)
            return get_peers()

        @app.route('/chain', methods=['GET'])
        def get_chain():
            chain_dict = {"length": len(
                self.chain.chain), "chain": self.chain.chain}
            return json.dumps(chain_dict, default=lambda obj: obj.__dict__)

        @app.route('/unmined_blocks', methods=['GET'])
        def get_unmined_blocks():
            chain_dict = {"unmined blocks": self.chain.unmined_chain}

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
            self.chain.add_transaction(transaction)
            return {"result": "Transaction added successfully"}, 200

        @app.route('/mine', methods=['GET'])
        def mine():
            if not self.chain.unmined_chain:
                return {'result': 'No unmined_blocks found'}, 200

            block_added = self.chain.mine()
            return {'result': block_added}, 200

        @app.route('/create_user', methods=['POST'])
        def create_user():
            user_data = request.get_json()
            required_fields = ['username', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    return {"result": "Invalid user data"}, 400

            user = User(user_data['username'], user_data['password'])

            for u in self.users:
                if u.username == user.username:
                    return {"result": "User already exists"}, 400

            self.users.append(user)

            file_path = f"{USER_DATA_DIR}/{user.username}.json"
            file = open(file_path, 'w')
            file.write(json.dumps(user.__dict__, indent=4))
            file.close()

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

            for user in self.users:
                if user['username'] == username and user[
                        'password'] == password:
                    return {"result": "User logged in successfully"}, 200

            return {"result": "Invalid username or password"}, 400

        app.run(host="0.0.0.0", port=8000)

    def consensus(self):
        for node in self.nodes.peers:
            if node == self.nodes.root_url:
                continue
            try:
                response = requests.get(node + 'chain')
                if response.status_code == 200:
                    json = response.json()

                    if json['length'] > len(self.chain.chain):
                        dicts = json['chain']
                        new_blocks: List[Block] = []
                        new_hashes: List[str] = []

                        prev_hash = '0'
                        valid_chain = True

                        for dict in dicts:
                            block = Block(transaction=dict['transaction'], nonce=dict['nonce'],
                                          prev_hash=dict['prev_hash'], timestamp=dict['timestamp'])

                            # check validity of the chain:
                            if prev_hash != block.prev_hash and dict['hash'] != block.compute_hash():
                                valid_chain = False
                                break

                            new_blocks.append(block)
                            new_hashes.append(dict['hash'])
                            prev_hash = dict['hash']

                        if valid_chain:
                            self.chain.replace_chain(new_blocks, new_hashes)
                            break
                    else:
                        # TODO: Check if both chains are identical
                        pass
            except Exception as e:
                print("Exception: ", e)
                self.nodes.failed_connect_peers.add(node)
