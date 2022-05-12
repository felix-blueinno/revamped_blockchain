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

            if "repl.co" in node_address:
                self.nodes.add_node(node_address)
                return get_peers(), 200
            else:
                return {"result": "Failed. We only accept repl node for now."}, 400

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

            # Get the latest chain & unmined chain:
            self.consensus()

            # Check presence of necessary fields:
            tx_data = request.get_json()
            required_fields = ['from', 'amount', 'to', 'password']
            for field in required_fields:
                if not tx_data.get(field):
                    return {"result": f"Missing field {field}"}, 400

            # Call /get_balance internally and check if user has enough balance:
            if tx_data['from'] != '_':
                response = requests.post(self.nodes.root_url + 'get_balance', json={'username': tx_data['from'],
                                                                                    'password': tx_data['password']})
                if response.status_code == 200:
                    balance = response.json()['balance']
                    balance -= tx_data['amount']
                    if balance < 0:
                        return {"result": "Failed. Insufficient balance."}, 400

                    # Make sure users won't declare multiple transactions that could lead to negative balance:
                    for ub in self.chain.unmined_chain:
                        tx = ub.transaction
                        if tx['from'] == tx_data['from']:
                            if balance >= tx_data['amount']:
                                balance -= tx['amount']
                            else:
                                return {"result": "Failed. Insufficient balance."}, 400
                else:
                    return {"result": response['result']}, 400

            self.chain.add_transaction(tx_data)
            self.announce()
            return {"result": "Transaction added successfully"}, 200

        @app.route('/mine', methods=['GET'])
        def mine():
            if not self.chain.unmined_chain:
                return {'result': 'No unmined_blocks found'}, 200

            block_added = self.chain.mine()

            if block_added:
                self.announce()
                return {'result': 'Block added successfully'}, 200

            return {'result': 'Block not added'}, 400

        @app.route('/update_chain', methods=['POST'])
        def update_chain():
            self.consensus()
            return {'result': 'Updating'}, 200

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
                if user.username == username and user.password == password:
                    return {"result": "User logged in successfully"}, 200

            return {"result": "Invalid username or password"}, 400

        @app.route('/get_balance', methods=['POST'])
        def get_balance():
            user_data = request.get_json()
            print(user_data)
            required_fields = ['username', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    return {"result": f"Missing field {field}"}, 400

            user_found = False
            for user in self.users:
                if user.username == user_data['username'] and user.password == user_data['password']:
                    balance = 0
                    for block in self.chain.chain:
                        tx = block.transaction
                        if tx['from'] == user_data['username']:
                            balance -= tx['amount']
                        if tx['to'] == user_data['username']:
                            balance += tx['amount']
                    user_found = True
                    break

            if not user_found:
                return {"result": "User not found"}, 400

            return {"balance": balance}, 200

        app.run(host="0.0.0.0", port=8000)

    def consensus(self):
        for node in self.nodes.peers:
            if node == self.nodes.root_url:
                continue
            try:
                response = requests.get(node + 'chain')
                if response.status_code == 200:
                    peer_json = response.json()

                    if peer_json['length'] >= len(self.chain.chain):
                        dicts = peer_json['chain']
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

                            response = requests.get(node + 'unmined_blocks')
                            if response.status_code == 200:
                                ub_json = response.json()
                                peer_ub_list = ub_json['unmined blocks']

                            if peer_json['length'] > len(self.chain.chain):
                                self.chain.replace_unmined_chain(peer_ub_list)
                            elif peer_json['length'] == len(self.chain.chain):
                                if len(peer_ub_list) > len(self.chain.unmined_chain):
                                    self.chain.replace_unmined_chain(
                                        peer_ub_list)
                            break

                    else:
                        # TODO: Check if both chains are identical
                        pass
            except Exception as e:
                print("Exception: ", e)
                self.nodes.failed_connect_peers.add(node)

    def announce(self):
        for node in self.nodes.peers:
            if node == self.nodes.root_url:
                continue
            try:
                response = requests.post(node + 'update_chain')
                if response.status_code == 200:
                    print("Announced to node: ", node)
            except Exception as e:
                print("Exception: ", e)
                self.nodes.failed_connect_peers.add(node)
