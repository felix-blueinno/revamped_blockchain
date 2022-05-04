from typing import List
from blockchain import Blockchain
from flask_server import FlaskServer

chain = Blockchain()
users: List[dict] = []

server = FlaskServer(chain=chain, users=users)
server.run()
