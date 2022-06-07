import os
from constants import NODES_FILENAME, MASTER_NODE
import requests
import _thread


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

        for peer in self.peers:
            try:
                print('knocking: ', peer)
                response = requests.get(f'{peer}peers', timeout=5)
                if response.status_code == 200:

                    peers = response.json()['peers']
                    new_peer = set()

                    for peer in peers:
                        new_peer.add(peer)
                    self.peers = self.peers.union(new_peer)
                    break

            except Exception as e:
                print('+---------------------------------------------')
                print('Error connecting to: ', peer, '\nError: ', e)
                print('+---------------------------------------------')
                self.failed_connect_peers.add(peer)

        self.peers = self.peers - self.failed_connect_peers
        print('+---------------------------------------------')
        print('self.failed_connect_peers: ', self.failed_connect_peers)
        print('+---------------------------------------------')
        print('self.peers: ', self.peers)
        print('+---------------------------------------------')

        def knock_peer(address: str):
            try:
                response = requests.post(address + 'register_node',
                                         json={"node_address": self.root_url},
                                         timeout=5)

                if response.status_code != 200:
                    self.failed_connect_peers.add(address)

            except Exception as e:
                print(e)
                self.failed_connect_peers.add(address)

        for peer in self.peers:
            print("Registering with: ", peer)
            _thread.start_new_thread(knock_peer, (peer, ))
