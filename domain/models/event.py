from abc import ABC
from datetime import datetime


class Event(ABC):
    def __init__(self, created: datetime):
        self.created = created


class DepositEvent(Event):
    def __init__(self, destination: str, amount: int, created: datetime = datetime.now()):
        super(DepositEvent, self).__init__(created=created)
        self.destination = destination
        self.amount = amount


class TransferEvent(Event):
    def __init__(self, destination: str, amount: int, origin: str, created: datetime = datetime.now()):
        super(TransferEvent, self).__init__(created=created)
        self.destination = destination
        self.amount = amount
        self.origin = origin


class WithdrawEvent(Event):
    def __init__(self, origin: str, amount: int, created: datetime = datetime.now()):
        super(WithdrawEvent, self).__init__(created=created)
        self.origin = origin
        self.amount = amount
