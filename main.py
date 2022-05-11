import os
from typing import List
from blockchain import Blockchain
from constants import USER_DATA_DIR
from flask_server import FlaskServer
import json

from user import User

chain = Blockchain()
users: List[User] = []

if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)
else:
    for filename in os.listdir(USER_DATA_DIR):
        file_path = f"{USER_DATA_DIR}/{filename}"
        with open(file_path, 'r') as f:
            user_data = json.loads(f.read())
            user = User(user_data['username'], user_data['password'])

            users.append(user)

server = FlaskServer(chain=chain, users=users)
server.run()
