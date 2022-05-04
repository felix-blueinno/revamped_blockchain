from blockchain import Blockchain
from flask import Flask
import json

app = Flask("app name")


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


chain = Blockchain()

chain.add_transaction("tx1")
chain.mine()
chain.show()

chain.add_transaction("tx2")
chain.mine()
chain.show()

app.run(host="0.0.0.0", port=8000)
