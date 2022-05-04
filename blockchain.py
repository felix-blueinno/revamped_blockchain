import json
from pprint import pprint
from typing import List
from block import Block
from constants import CHAIN_DATA_DIR, FILE_HEADERS


class Blockchain:
    DIFFICULTY = 4

    def __init__(self):
        self.chain: List[Block] = []
        self.unmined_chain: List[Block] = []

    def create_genesis_block(self):
        self.add_transaction("genesis_block")
        self.mine(genesis_block=True)

    def add_block(self, block: Block, proof: str) -> bool:
        if self.verify_proof(block, proof):
            block.hash = proof
            self.chain.append(block)
            self.save_block_file(block)

            if block in self.unmined_chain:
                self.unmined_chain.remove(block)

            print(f"Block #{len(self.chain)-1} appended")
            return True
        else:
            print("Incorrect proof!")
            return False

    def verify_proof(self, block: Block, hash_proof: str):
        return hash_proof == block.compute_hash() and hash_proof.startswith('0' * self.DIFFICULTY)

    def add_transaction(self, transaction: str):
        unmined_block = Block(transaction=transaction, nonce=0)
        self.unmined_chain.append(unmined_block)

    def mine(self, genesis_block=False) -> bool:
        if not self.unmined_chain:
            return 'No unmined transaction'

        block = self.unmined_chain[0]

        if not genesis_block:
            block.prev_hash = self.chain[-1].hash

        proof = block.compute_hash()

        while not self.verify_proof(block, proof):
            block.nonce += 1
            proof = block.compute_hash()

        block_added = self.add_block(block, proof)
        return block_added

    def save_block_file(self, block: Block):

        block_id = len(self.chain)
        content = json.dumps(block.__dict__, indent=4)

        file_path = f"{CHAIN_DATA_DIR}/{FILE_HEADERS}{block_id}.json"
        file = open(file_path, 'w')
        file.write(content)
        file.close()

    def show(self):
        print(
            "+---------------------------------------------------------------------------")
        for block in self.chain:
            pprint(block.__dict__)
        print(
            "+---------------------------------------------------------------------------")
