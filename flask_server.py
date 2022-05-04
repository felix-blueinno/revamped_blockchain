import json
from flask import Flask, request
from blockchain import Blockchain


class FlaskServer:
    def __init__(self, chain: Blockchain,
                 users: list,
                 server_name: str = "app",
                 port: int = 8000,):
        self.chain = chain
        self.users = users

        self.server_name = server_name
        self.port = port

    def run(self):
        app = Flask("app name")

        @app.route("/")
        def homepage():
            return f'we have {len(self.chain.chain)} blocks now.'

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

            username = user_data['username']
            password = user_data['password']

            for u in self.users:
                if u['username'] == username:
                    return {"result": "User already exists"}, 400

            user = {'username': username, 'password': password}
            self.users.append(user)
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
