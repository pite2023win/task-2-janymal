#!/usr/bin/env python3

from uuid import uuid4 as generate_uuid


class Account:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = 0

    def input(self, amount: float):
        self.balance += amount

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("the amount greater than the balance")
        self.balance -= amount


class Bank:
    def __init__(self, name: str):
        self.name = name
        self.accounts = {}

    def create_account(self, first_name: str, last_name: str):
        new_account = Account(first_name, last_name)
        new_account_address = generate_uuid().hex
        while new_account_address in self.accounts.keys:
            new_account_address = generate_uuid().hex
        self.accounts[new_account_address] = new_account

    def transfer(self, form_address: str, to_address: str, amount: float):
        if from_address not in self.accounts.keys:
            raise ValueError("from address not found")
        if to_address not in self.accounts.keys:
            raise ValueError("to address not found")
        self.accounts[from_address].withdraw(amount)
        self.accounts[to_address].input(amount)


if __name__ == "__main__":
    pass
