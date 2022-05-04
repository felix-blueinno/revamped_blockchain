from block import Block
from blockchain import Blockchain

chain = Blockchain()

block = Block(transaction='tx1', nonce=0, prev_hash=chain.chain[-1].hash )
proof = block.compute_hash()

chain.add_block(block,  proof +'hey!' )
chain.add_block(block,  proof)

chain.show()
