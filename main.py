from pprint import pprint
import hashlib
import time

# Create an empty blockchain
chain = []

def compute_hash(block: dict) -> str:
    return hashlib.sha256(str(block).encode()).hexdigest()

def add_block(tx_data: str):
    global chain
    prev_hash = chain[-1]["hash"] if len(chain) > 0 else "0" * 64
    block = {"transaction": tx_data, "prev_hash": prev_hash,
             "nonce": 0, "timestamp": time.time()}
    block["hash"] = compute_hash(block)
    chain.append(block)

while True:
    tx_data = input("Transaction data: ")
    add_block(tx_data)
    pprint(chain)
