from pprint import pprint
from typing import List
from block import Block


class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        first_block = Block("genesis_block", 0)
        first_block.hash = first_block.compute_hash()
        self.chain.append(first_block)

    def add_block(self, block: Block, proof: str):
        if self.verify_proof(block, proof):
            block.hash = proof
            self.chain.append(block)
            print(f"Block #{len(self.chain)-1} appended")
        else:
            print("Incorrect proof!")
            
    def verify_proof(self, block: Block, hash_proof: str) -> bool:
        return hash_proof == block.compute_hash()
        
    def show(self):
        print("+---------------------------------------------------------------------------")
        for block in self.chain:
            pprint(block.__dict__)
        print("+---------------------------------------------------------------------------")
