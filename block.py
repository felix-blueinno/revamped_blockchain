import time
import hashlib


class Block:
    def __init__(self, transaction: dict, nonce: int, prev_hash: str = "0", timestamp=0):
        self.transaction = transaction
        self.nonce = nonce
        self.timestamp = timestamp if timestamp != 0 else time.time()
        self.prev_hash = prev_hash
        self.hash: str = ""

    def compute_hash(self) -> str:
        class_str = str(self.__dict__)
        encoded_str = str.encode(class_str)
        return hashlib.sha256(encoded_str).hexdigest()
