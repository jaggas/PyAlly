from __future__ import annotations
import xml.etree.ElementTree as ET
import enum
import pendulum as pdl
import numpy as np


def fixTag(tag):
    return tag.split("}", 1)[-1]

def parseTree(tree):

    if isinstance(tree, str):
        tree = ET.fromstring(tree)

    if tree is None:
        return {}

    x = tree.attrib

    for child in tree:
        key = child.tag.split('}')[1]
        x[key] = parseTree(child)

    return x

TEST1 = '<?xml version="1.0" encoding="utf-8"?>\r\n<FIXML xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2">\r\n  <ExecRpt OrdID="SVI-6214055216" ID="SVI-6214055216" Stat="4" Acct="3LB700351" AcctTyp="1" Side="2" Typ="2" Px="85.0" TmInForce="0" LeavesQty="1.0" TrdDt="2022-11-20T15:13:00.000-05:00" TxnTm="2022-11-20T15:13:00.000-05:00" Txt="Canceled by user">\r\n    <Instrmt Sym="TSM" SecTyp="CS" Desc="TAIWAN SEMICONDUCTOR MFG CO" />\r\n    <OrdQty Qty="1" />\r\n    <Comm Comm="0.00" />\r\n  </ExecRpt>\r\n</FIXML>'

class OrderStatus(enum.Enum):
    """Current status of order
    https://schemas.liquid-technologies.com/fixml/5.0sp2/?page=ordstatus_enum_t.html
    """
    NEW = "0"
    PARTIALLY_FILLED = "1"
    FILLED = "2"
    DONE_FOR_DAY = "3"
    CANCELED = "4"
    PENDING_CANCEL = "6"
    STOPPED = "7"
    REJECTED = "8"
    SUSPENDED = "9"
    PENDING_NEW = "A"
    CALCULATED = "B"
    EXPIRED = "C"
    ACCEPTED_FOR_BIDDING = "D"
    PENDING_REPLACE = "E"

class Side(enum.Enum):
    """Order side
    https://schemas.liquid-technologies.com/fixml/5.0sp2/side_enum_t.html 
    """
    BUY = "1"
    SELL = "2"
    SELL_SHORT = "5"
    
class OrderType(enum.Enum):
    """Order type
    https://schemas.liquid-technologies.com/fixml/5.0sp2/ordtype_enum_t.html 
    """
    MARKET = "1"
    LIMIT = "2"
    STOP = "3"
    STOP_LIMIT = "4"
    STOP_LOSS = "5"
    TRAILING_STOP = "6"
    
class TimeInForce(enum.Enum):
    """Time in force or order
    https://schemas.liquid-technologies.com/fixml/5.0sp2/?page=timeinforce_enum_t.html
    """
    DAY = "0"
    GTC = "1"
    ATC = "7"  # Market on Close, not valid with Type == MARKET

class Pricing:
    def __init__(self, order_type: OrderType):
        self.order_type: OrderType = order_type

    @property
    def fixml(self) -> dict:
        return {"Typ": self.order_type.value}

class Market(Pricing):
    def __init__(self):
        super().__init__(OrderType.MARKET)

class Limit(Pricing):
    def __init__(self, limit_price: float):
        super().__init__(OrderType.LIMIT)
        self.px = round(float(limit_price), 2)
    
    @property
    def fixml(self) -> str:
        return {**super().fixml, "Px": str(self.px)}

class Stop(Pricing):
    def __init__(self, stop_price: float):
        super().__init__(OrderType.STOP_LIMIT)
        self.stop_px = round(float(stop_price), 2)

    @property
    def fixml(self) -> str:
        return {**super().fixml, "StopPx": str(self.stop_px)}


class StopLimit(Pricing):
    def __init__(self, limit_price: float, stop_price: float):
        """Stop-limit price object.
        Args:
                limpx: limit price, to be used once stop price was reached
                stoppx: stop price, to trigger limit price
        """
        super().__init__(OrderType.STOP_LIMIT)
        self.px = round(float(limit_price), 2)
        self.stop_px = round(float(stop_price), 2)
        
    @property
    def fixml(self) -> str:
        return {**super().fixml, "StopPx": str(self.stop_px), "Px": str(self.px)}

class FIXMLMessage:
    def __init__(self, fixml: str):
        self.raw = list(parseTree(fixml).values())[0]

class Product:
    """Traded product info.
    https://schemas.liquid-technologies.com/fixml/5.0sp2/?page=instrument_block_t.html
    """
    def __init__(self, fixml_d: dict):
        self.symbol: str = fixml_d['Sym']
        assert(fixml_d['SecTyp'] == 'CS')
        self.description: str = fixml_d.get('Desc', None)

class FillInfo:
    """Order fill info
    https://schemas.liquid-technologies.com/fixml/5.0sp2/?page=fillsgrp_block_t.html
    """
    def __init__(self, fixml_d: dict):
        self.fill_qty = int(fixml_d['FillQty'])
        self.fill_price = float(fixml_d['FillPx'])
        
class ExecReport(FIXMLMessage):
    """Order response/status message.
    https://schemas.liquid-technologies.com/fixml/5.0sp2/?page=executionreport_message_t.html
    """
    def __init__(self, fixml: str):
        super().__init__(fixml)
        
    @property
    def order_id(self) -> str:
        """Unique identifier for Order as assigned by sell-side (broker, exchange, ECN). Uniqueness must be guaranteed within a single trading day. Firms"""
        return self.raw['OrdID']
    
    @property
    def client_order_id(self) -> str:
        """Unique identifier for Order as assigned by the buy-side (institution, broker, intermediary etc.)"""
        return self.raw['ID']
    
    @property
    def order_status(self) -> OrderStatus:
        return OrderStatus(self.raw['Stat'])
    
    @property
    def account(self) -> str:
        return self.raw['Acct']
    
    @property
    def side(self) -> Side:
        return Side(self.raw['Side'])
    
    @property
    def order_type(self) -> OrderType:
        return OrderType(self.raw['Typ'])

    @property
    def time_in_force(self) -> TimeInForce:
        return TimeInForce(self.raw['TmInForce'])
    
    @property
    def price(self) -> float:
        return float(self.raw['Px'])
    
    @property
    def last_price(self) -> float:
        return float(self.raw.get('LastPx', np.nan))
    
    @property
    def average_price(self) -> float:
        return float(self.raw.get('AvgPx', np.nan))
    
    @property
    def qty(self) -> int:
        return int(self.raw['OrdQty']['Qty'])
    
    @property
    def last_qty(self) -> int:
        return int(self.raw.get('LastQty', 0))

    @property
    def fill_qty(self) -> int:
        return int(self.ra)

    @property
    def cumulative_qty(self) -> int:
        return int(self.raw.get('CumQty', 0))
    
    @property
    def product(self) -> Product:
        return Product(self.raw['Instrmt'])
    
    @property
    def remaining_qty(self) -> int:
        return int(self.raw.get('LeavesQty', 0))
    
    @property
    def timestamp(self) -> pdl.datetime:
        return pdl.parse(self.raw['TxnTm'])
    
    @property
    def message(self) -> str:
        return self.raw.get('Txt', None)
    
    @property
    def fill_info(self) -> FillInfo:
        fill_d = self.raw.get('FillsGrp', None)
        return FillInfo(self.raw.get('FillsGrp', {})) if fill_d else None

class OrderTemplate:
    def __init__(self):
        self.account: str = None
        self.product: Product = None
        self.order_id: str = None
        self.price: Pricing = None
        self.side: Side = None
        self.time_in_force: TimeInForce = None
    
    def set_account(self, account: str):
        self.account = account
    
    def set_product(self, product: Product):
        self.product = product
    
    def set_order_id(self, order_id: str):
        self.order_id = order_id
    
    def set_pricing(self, pricing: Pricing):
        self.pricing =  pricing 

    def set_side(self, side: Side):
        self.side = side
        
    def set_time_in_force(self, time_in_force: TimeInForce):
        self.time_in_force = time_in_force
        
    def set_order_type(self, order_type: OrderType):
        self.order_type = order_type

class OrderCancel(OrderTemplate):
    def __init__(self):
        self.set_time_in_force(TimeInForce.DAY)
        
execRpt = ExecReport(TEST1)
fill_info = execRpt.fill_info
t = execRpt.order_status
qty = execRpt.qty
cqty = execRpt.cumulative_qty
print(str(t))
p = execRpt.product
status = execRpt.order_status
side = execRpt.side
tif = execRpt.time_in_force
typ = execRpt.order_type
price = execRpt.price

i = 1