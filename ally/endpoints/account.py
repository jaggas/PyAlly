from __future__ import annotations
import enum
from typing import Dict, List
import json

class Model:
    def __init__(self, response: dict):
        self._response = response
    
    def __getitem__(self, attr: str):
        return self._response[attr]

    def to_dict(self) -> dict:
        filter_lambda = lambda x: x[0] != '_' and not callable(getattr(self, x, None))
        property_l = list(filter(filter_lambda, dir(self)))
        return {prop: getattr(self, prop) for prop in property_l}
             
class Account(Model):
    def __init__(self, response: dict):
        super().__init__(response)
    
    @property
    def account_number(self) -> str:
        return self['account']
    
    @property
    def value(self) -> float:
        return float(self['accountvalue'])
    
    @property
    def cash_available_for_withdrawal(self) -> float:
        """Cash available for withdrawal (cash & margin accounts only, n/a for retirement accounts)"""
        return float(self['buyingpower']['cashavailableforwithdrawal'])
    

class HoldingType(enum.Enum):
    CASH = 1
    MARGIN_LONG = 2
    MARGIN_SHORT = 5


class BuyingPower(Model):
    def __init__(self, response: dict):
        super().__init__(response)
    
    @property
    def cash_available_for_withdrawal(self) -> float:
        """Cash available for withdrawal (cash & margin accounts only, n/a for retirement accounts)"""
        return float(self.cashavailableforwithdrawal)

    @property
    def day_trading(self) -> float:
        return float(self.daytrading)

    @property
    def options(self) -> float:
        """Options buying power"""
        return float(self.options)

    @property
    def options_start_of_day(self) -> float:
        """Start of day options buying power"""
        return float(self.sodoptions)

    @property
    def stock(self) -> float:
        """Stock buying power"""
        return float(self['stock'])

    @property
    def stock_start_of_day(self) -> float:
        """Start of day stock buying power"""
        return float(self.sodstock)

class Money(Model):
    def __init__(self, response: dict):
        super().__init__(response)

class Securities(Model):
    def __init__(self, response: dict):
        super().__init__(response)

class Holding(Model):
    def __init__(self, response: dict):
        super().__init__(response)
    
    @property
    def symbol(self) -> str:
        return self.displaydata['symbol']

class AccountBalance(Model):
    def __init__(self, response: dict):
        super().__init__(response)
        self.buying_power = BuyingPower(self.buyingpower)
        self.money = Money(self.money)
        self.securities = Securities(self.securities)

class Account2(Model):
    def __init__(self, response: dict):
        super().__init__(response['accounts']['accountsummary'])
        self.balance = AccountBalance(self.accountbalance)
        self.positions: Dict[str, Holding] = {}
        for holding_d in self.accountholdings['holding']:
            position = Holding(holding_d)
            self.positions[position.symbol] = position


        print()

    @property
    def account_value(self) -> float:
        return 

'''
with open('response.json', 'r') as fp:
    response = json.load(fp)

acct = Account2(response['response'])

print()'''