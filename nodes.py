import os
from constants import NODES_FILENAME, MASTER_NODE


class Nodes:
    def __init__(self):
        self.peers = set()
        self.failed_connect_peers = set()
        self.root_url = ''

        if not os.path.exists(NODES_FILENAME):
            self.add_node(MASTER_NODE)
        else:
            with open(NODES_FILENAME, 'r') as f:
                content = f.read()
                self.peers = set(content.split(','))
                self.peers.discard('')
                f.close()

    def add_node(self, node: str):
        self.peers.add(node)
        with open(NODES_FILENAME, 'w') as f:
            for peer in self.peers:
                f.write(peer + ',')

    def knock_peers(self):
        pass
