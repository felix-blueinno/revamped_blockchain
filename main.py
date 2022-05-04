from blockchain import Blockchain
from flask import Flask

app = Flask("app name")

@app.route("/")
def homepage():
    return "Hello there~~~"

chain = Blockchain()

chain.add_transaction("tx1")
chain.mine()
chain.show()

chain.add_transaction("tx2")
chain.mine()
chain.show()

app.run(host="0.0.0.0", port=8000)