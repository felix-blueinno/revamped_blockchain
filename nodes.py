import os
from constants import NODES_FILENAME, MASTER_NODE
import requests


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
        new_peers = set()
        for peer in self.peers:
            try:
                response = requests.get(f'{peer}/peers')
                if response.status_code == 200:
                    peers = response.json()['peers']
                    for peer in peers:
                        new_peers.add(peer)
                    break

            except Exception as e:
                print("Exception occurs: ", e)
                self.failed_connect_peers.add(peer)

        self.peers = self.peers.union(new_peers)

        for peer in self.peers:
            try:
                response = requests.post(peer + 'register_node',
                                         json={"node_address": self.root_url})

                if response.status_code != 200:
                    self.failed_connect_peers.add(peer)

            except Exception as e:
                print(e)
                self.failed_connect_peers.add(peer)
