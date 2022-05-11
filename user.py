from __future__ import annotations


class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def withdraw(self):
        pass

    def deposit(self):
        pass

    def transfer(self, amount: float, recipient: User):
        pass
