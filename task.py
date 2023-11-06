#!/usr/bin/env python3

# use thread or multiprocessing or asyncio

# I couldn't find a good use for async
# Using it for file loading makes code a spaghetti
# import asyncio

from argparse import ArgumentParser
from random import choice
from string import digits
import json
import logging


class Account:
    _logger = logging.getLogger("account")

    def log_info(self):
        message = "Account details: (first name: {first_name}, last name: {last_name}, balance: {balance})"
        self._logger.info(
            message.format(
                first_name=self._first_name,
                last_name=self._last_name,
                balance=self._balance,
            )
        )

    def _debug_message(func):
        def wrapper(self, *args, **kwargs):
            self._logger.debug("Calling {name}".format(name=func.__name__))
            return_value = func(self, *args, **kwargs)
            self._logger.debug("Exiting {name}".format(name=func.__name__))
            return return_value

        return wrapper

    @staticmethod
    def generate_number(length=26):
        return "".join(choice(digits) for i in range(length))

    @_debug_message
    def __init__(self, first_name: str, last_name: str, balance: float = 0):
        self._first_name = first_name
        self._last_name = last_name
        self._balance = balance

    @classmethod
    def from_dict(cls, dictionary):
        # unsafe variant
        # return cls(*dictionary.values())
        return cls(
            dictionary["first_name"], dictionary["last_name"], dictionary["balance"]
        )

    @_debug_message
    def to_dict(self):
        return {
            "first_name": self._first_name,
            "last_name": self._last_name,
            "balance": self._balance,
        }

    @_debug_message
    def input(self, amount: float):
        self._balance += amount

    @_debug_message
    def withdraw(self, amount: float):
        if amount > self._balance:
            raise ValueError("the amount greater than the balance")
        self._balance -= amount


class Bank:
    _logger = logging.getLogger("bank")

    def __init__(self, name: str, accounts={}):
        self._name = name
        self._accounts = accounts

    @classmethod
    def from_dict(cls, dictionary):
        accounts = {}
        for key in dictionary["accounts"].keys():
            if not key.isnumeric() or len(key) != 26:
                raise ValueError("wrong account number: {number}".format(number=key))
            accounts[key] = Account.from_dict(dictionary["accounts"][key])
        return cls(dictionary["name"], accounts)

    @classmethod
    def from_file(cls, filepath: str):
        with open(filepath, "r") as file:
            return cls.from_dict(json.loads(file.read()))

    def to_dict(self):
        dictionary = {"name": self._name, "accounts": {}}
        for key in self._accounts.keys():
            dictionary["accounts"][key] = self._accounts[key].to_dict()
        return dictionary

    def to_file(self, path: str):
        write_file_message = "Writing file to {path}"
        with open(path, "w") as file:
            dictionary = self.to_dict()
            json_formatted = json.dumps(dictionary, indent=4)
            self._logger.info(write_file_message.format(path=path))
            file.write(json_formatted)

    def create_account(self, first_name: str, last_name: str):
        account = Account(first_name, last_name)
        is_number_taken = True
        while is_number_taken:
            account_number = Account.generate_number()
            if account_number not in self._accounts.keys():
                is_number_taken = False
        self._accounts[account_number] = account
        self._logger.info("Account with {number} number crated".format(number=account_number))
        return account_number


    def transfer_money(self, sender_number: str, recipient_number: str, amount: float):
        if sender_number not in self._accounts.keys():
            raise ValueError("sender not found")
        if recipient_number not in self._accounts.keys():
            raise ValueError("recipient not found")
        self._accounts[sender_number].withdraw(amount)
        self._accounts[recipient_number].input(amount)

    def log_all(self):
        name_message = "Name of the bank: {name}"
        self._logger.info(name_message.format(name=self._name))
        for key in self._accounts.keys():
            account_message = "Getting account of number: {number}"
            self._logger.info(account_message.format(number=key))
            self._accounts[key].log_info()

    def get_account(self, number: str):
        return self._accounts[number]


def demo():
    logging.basicConfig(level=logging.DEBUG)
    try:
        demo_bank = Bank.from_file("demo_wrong.json")
    except Exception as e:
        logging.error(e)
    demo_bank = Bank.from_file("demo.json")
    second_bank = Bank("Pekao")
    john_doe_account = second_bank.create_account("John", "Doe")
    abc_xyz_account = second_bank.create_account("Abc", "Xyz")
    second_bank.get_account(john_doe_account).input(10)
    second_bank.get_account(abc_xyz_account).input(420.01)
    second_bank.get_account(abc_xyz_account).withdraw(20.01)
    second_bank.log_all_accounts()
    demo_bank.transfer_money("51956445405539334529285918", "64278787073145255302999030", 21.37)
    demo_bank.log_all_accounts()
    demo_bank.to_file("demo_output1.json")
    second_bank.to_file("demo_output2.json")


def interactive():
    logging.basicConfig(level=logging.INFO)
    bank = None

    def check_bank_instance():
        if not isinstance(bank, Bank):
            raise TypeError("Bank instance has not been set up")

    is_running = True
    while is_running:
        line = input("> ").split()
        try:
            if line[0] in ["i", "input"]:
                check_bank_instance()
                bank.get_account(line[1]).input(float(line[2]))
            elif line[0] in ["w", "withdraw"]:
                check_bank_instance()
                bank.get_account(line[1]).withdraw(float(line[2]))
            elif line[0] in ["t", "transfer"]:
                check_bank_instance()
                bank.transfer_money(line[1], line[2], float(line[3]))
            elif line[0] in ["n", "new"]:
                bank = Bank(line[1])
            elif line[0] in ["c", "create"]:
                check_bank_instance()
                bank.create_account(line[1], line[2])
            elif line[0] in ["l", "load"]:
                bank = Bank.from_file(line[1])
            elif line[0] in ["s", "save"]:
                check_bank_instance()
                bank.to_file(line[1])
            elif line[0] in ["p", "print"]:
                check_bank_instance()
                bank.log_all()
            elif line[0] in ["g", "generate"]:
                message = "account number: {number}"
                logging.info(message.format(number=Account.generate_number()))
            elif line[0] in ["q", "e", "exit", "quit"]:
                is_running = False
            else:
                raise ValueError("Unknown command '{command}'".format(command=line[0]))
        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="Bank Accounts Manager", description="Does what the name says"
    )
    parser.add_argument("mode", choices=["interactive", "demo", "generator"])
    # parser.add_argument("filename", nargs="*")
    args = parser.parse_args()
    if args.mode == "demo":
        demo()
    elif args.mode == "interactive":
        interactive()
    elif args.mode == "generator":
        # CLI element, so I use print instead of logging here
        print(Account.generate_number())
