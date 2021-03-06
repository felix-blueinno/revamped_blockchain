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
        self.add_transaction({'from': '_', 'to': '_', 'amount': 0})
        self.mine(genesis_block=True)

    def add_block(self, block: Block, proof: str) -> bool:
        if self.verify_proof(block, proof):
            block.hash = proof
            self.chain.append(block)
            self.save_block_file(block)

            for ub in self.unmined_chain:
                if block.timestamp == ub.timestamp:
                    self.unmined_chain.remove(ub)
                    break

            for filename in os.listdir(UNMINED_DATA_DIR):
                # load file as json
                with open(f'{UNMINED_DATA_DIR}/{filename}') as ub_file:
                    data = json.load(ub_file)
                    if data['timestamp'] == block.timestamp:
                        os.remove(f'{UNMINED_DATA_DIR}/{filename}')
                        break

            print(f"Block #{len(self.chain)-1} appended")
            return True
        else:
            print("Incorrect proof!")
            return False

    def verify_proof(self, block: Block, hash_proof: str):
        if len(self.chain) != 0 and block.prev_hash != self.chain[-1].hash:
            return False
        return hash_proof == block.compute_hash() and hash_proof.startswith('0000')

    def add_transaction(self, transaction: dict, timestamp: float = 0):
        unmined_block = Block(transaction=transaction,
                              nonce=0,
                              timestamp=timestamp,)
        self.unmined_chain.append(unmined_block)

        content = json.dumps(unmined_block.__dict__, indent=4)

        file_id = len(self.chain) + len(self.unmined_chain)
        file = open(f'{UNMINED_DATA_DIR}/{file_id}.json', 'w')
        file.write(content)
        file.close()

    def mine(self, genesis_block=False) -> bool:

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
            def sort_file(s):
                return int(s.split('.')[0])
            for filename in sorted(os.listdir(UNMINED_DATA_DIR), key=sort_file):
                with open(f'{UNMINED_DATA_DIR}/{filename}') as ub_file:
                    data = json.load(ub_file)
                    block = Block(data['transaction'], data['nonce'],
                                  data['prev_hash'], data['timestamp'])
                    self.unmined_chain.append(block)

    def init_mined_chain(self):
        if not os.path.exists(CHAIN_DATA_DIR):
            os.mkdir(CHAIN_DATA_DIR)
            self.create_genesis_block()

        elif not os.listdir(CHAIN_DATA_DIR) == []:
            def sort_file(s):
                return int(s.split('.')[0])
            all_files = sorted(os.listdir(CHAIN_DATA_DIR), key=sort_file)
            for filename in all_files:
                with open(f'{CHAIN_DATA_DIR}/{filename}') as json_file:
                    data = json.load(json_file)
                    block = Block(data['transaction'],
                                  data['nonce'],
                                  data['prev_hash'],
                                  data['timestamp'])

                    proof = data['hash']
                    added = self.add_block(block, proof)
                    if not added:
                        print(f"{filename} is tampered")
                        # TODO:
                        break

    def replace_chain(self, chain: List[Block], hashes: List[str]):

        self.chain.clear()

        for i in range(len(chain)):
            self.add_block(chain[i], hashes[i])

    def replace_unmined_chain(self, unmined_list: List[dict]):
        self.unmined_chain.clear()

        for file in os.listdir(UNMINED_DATA_DIR):
            os.remove(os.path.join(
                UNMINED_DATA_DIR, file))

        for unmined_block in unmined_list:
            tx_data = unmined_block['transaction']
            timestamp = unmined_block['timestamp']
            self.add_transaction(tx_data, timestamp)
