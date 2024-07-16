from typing import List

from domain.models.event import DepositEvent, TransferEvent, WithdrawEvent
from domain.repositories.EventRepository import DepositEventRepository, TransferEventRepository, WithdrawEventRepository


class LocalDepositEventRepository(DepositEventRepository):
    def __init__(self, local_data_source: List[DepositEvent]):
        self._deposit_events_data_source = local_data_source

    def filter_by_destination_id(self, id) -> List[DepositEvent]:
        return list(filter(lambda x: x.destination == id, self._deposit_events_data_source))

    def save(self, deposit_event: DepositEvent) -> DepositEvent:
        self._deposit_events_data_source.append(deposit_event)
        return deposit_event


class LocalTransferEventRepository(TransferEventRepository):
    def __init__(self, local_data_source: List[TransferEvent]):
        self._transfer_events_data_source = local_data_source

    def filter_by_destination_id(self, id) -> List[TransferEvent]:
        return list(filter(lambda x: x.destination == id, self._transfer_events_data_source))

    def filter_by_origin_id(self, id) -> List[TransferEvent]:
        return list(filter(lambda x: x.origin == id, self._transfer_events_data_source))

    def save(self, transfer_event: TransferEvent) -> TransferEvent:
        self._transfer_events_data_source.append(transfer_event)
        return transfer_event


class LocalWithdrawEventRepository(WithdrawEventRepository):
    def __init__(self, local_data_source: List[WithdrawEvent]):
        self._withdraw_events_data_source = local_data_source

    def filter_by_origin_id(self, id) -> List[WithdrawEvent]:
        return list(filter(lambda x: x.origin == id, self._withdraw_events_data_source))

    def save(self, withdraw_event: WithdrawEvent) -> WithdrawEvent:
        self._withdraw_events_data_source.append(withdraw_event)
        return withdraw_event
