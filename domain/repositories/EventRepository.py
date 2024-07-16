from abc import ABC, abstractmethod
from typing import List

from domain.models.event import DepositEvent, TransferEvent, WithdrawEvent


class DepositEventRepository(ABC):

    @abstractmethod
    def filter_by_destination_id(self, id) -> List[DepositEvent]:
        pass

    @abstractmethod
    def save(self, deposit_event: DepositEvent) -> DepositEvent:
        pass


class TransferEventRepository(ABC):

    @abstractmethod
    def filter_by_destination_id(self, id) -> List[TransferEvent]:
        pass

    @abstractmethod
    def filter_by_origin_id(self, id) -> List[TransferEvent]:
        pass

    @abstractmethod
    def save(self, deposit_event: TransferEvent) -> TransferEvent:
        pass


class WithdrawEventRepository(ABC):

    @abstractmethod
    def filter_by_origin_id(self, id) -> List[WithdrawEvent]:
        pass

    @abstractmethod
    def save(self, deposit_event: WithdrawEvent) -> WithdrawEvent:
        pass
