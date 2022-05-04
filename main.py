from blockchain import Blockchain

chain = Blockchain()

chain.add_transaction("tx1")
chain.mine()
chain.show()

chain.add_transaction("tx2")
chain.mine()
chain.show()

