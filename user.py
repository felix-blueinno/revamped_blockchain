from __future__ import annotations


class User:
    def __init__(self, username: str, password: str, balance: float = 0):
        self.username = username
        self.password = password
        self.balance = balance

    def withdraw(self):
        pass

    def deposit(self):
        pass

    def transfer(self, amount: float, recipient: User):
        pass
