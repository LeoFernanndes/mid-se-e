from abc import ABC
from datetime import datetime


class Event(ABC):
    def __init__(self, created: datetime, amount: int):
        self.created = created
        self.amount = amount


class DepositEvent(Event):
    def __init__(self, destination: str, amount: int, created: datetime):
        super(DepositEvent, self).__init__(created=created, amount=amount)
        self.destination = destination


class TransferEvent(Event):
    def __init__(self, destination: str, amount: int, origin: str, created: datetime):
        super(TransferEvent, self).__init__(created=created, amount=amount)
        self.destination = destination
        self.origin = origin


class WithdrawEvent(Event):
    def __init__(self, origin: str, amount: int, created: datetime):
        super(WithdrawEvent, self).__init__(created=created, amount=amount)
        self.origin = origin

