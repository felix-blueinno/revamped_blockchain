import json
import os
from pprint import pprint
from typing import List
from block import Block
from constants import CHAIN_DATA_DIR, FILE_HEADERS, UNMINED_DATA_DIR


class Blockchain:
    DIFFICULTY = 4

    def __init__(self):
        self.chain: List[Block] = []
        self.unmined_chain: List[Block] = []

        self.init_unmined_chain()
        self.init_mined_chain()

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
                block_id = len(self.chain)
                os.remove(f"{UNMINED_DATA_DIR}/{block_id}.json")

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

        content = json.dumps(unmined_block.__dict__, indent=4)

        file_id = len(self.chain) + len(self.unmined_chain)
        file = open(f'{UNMINED_DATA_DIR}/{file_id}.json', 'w')
        file.write(content)
        file.close()

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

    def init_unmined_chain(self):
        if not os.path.exists(UNMINED_DATA_DIR):
            os.mkdir(UNMINED_DATA_DIR)
        else:
            for filename in sorted(os.listdir(UNMINED_DATA_DIR)):
                with open(f'{UNMINED_DATA_DIR}/{filename}') as ub_file:
                    data = json.load(ub_file)
                    block = Block(data['transaction'], data['nonce'],
                                  data['prev_hash'], data['timestamp'])
                    self.chain.unmined_chain.append(block)

    def init_mined_chain(self):
        if not os.path.exists(CHAIN_DATA_DIR):
            os.mkdir(CHAIN_DATA_DIR)
            self.create_genesis_block()

        elif not os.listdir(CHAIN_DATA_DIR) == []:
            all_files = sorted(os.listdir(CHAIN_DATA_DIR))
            for filename in all_files:
                with open(f'{CHAIN_DATA_DIR}/{filename}') as json_file:
                    data = json.load(json_file)
                    block = Block(data['transaction'],
                                  data['nonce'],
                                  data['prev_hash'],
                                  data['timestamp'])

                    proof = data['hash']
                    self.add_block(block, proof)
