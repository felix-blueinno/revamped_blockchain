from typing import List
from blockchain import Blockchain
from flask_server import FlaskServer

chain = Blockchain()
users: List[dict] = []


chain = Blockchain()
users = []

server = FlaskServer(chain=chain, users=users)
server.run()
