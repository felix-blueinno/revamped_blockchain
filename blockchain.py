from pprint import pprint
from typing import List
from block import Block


class Blockchain:
    DIFFICULTY = 4

    def __init__(self):
        self.chain: List[Block] = []
        self.unmined_chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        self.add_transaction("genesis_block")
        self.mine(genesis_block=True)

    def add_block(self, block: Block, proof: str):
        if self.verify_proof(block, proof):
            block.hash = proof
            self.chain.append(block)
            
            if block in self.unmined_chain:
                self.unmined_chain.remove(block)

            print(f"Block #{len(self.chain)-1} appended")
        else:
            print("Incorrect proof!")
            
    def verify_proof(self, block: Block, hash_proof: str):
        return hash_proof == block.compute_hash() and hash_proof.startswith('0' * self.DIFFICULTY)
    
    def add_transaction(self, transaction: str):
        unmined_block = Block(transaction=transaction, nonce=0)
        self.unmined_chain.append(unmined_block)

    def mine(self, genesis_block=False ):
        if not self.unmined_chain:
            return 'No unmined transaction'

        block = self.unmined_chain[0]
        block.prev_hash = self.chain[-1].hash

        if not genesis_block:
            block.prev_hash = self.chain[-1].hash

        proof = block.compute_hash()

        while not self.verify_proof(block, proof):
            block.nonce += 1
            proof = block.compute_hash()
        self.add_block(block, proof)

    def show(self):
        print("+---------------------------------------------------------------------------")
        for block in self.chain:
            pprint(block.__dict__)
        print("+---------------------------------------------------------------------------")
