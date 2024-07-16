import copy

from datetime import datetime
from typing import List, Union

from application.dto.account import AccountDto
from application.dto.event import (DepositInputDto, DepositOutputDto, TransferInputDto, TransferOutputDto,
                                   WithdrawInputDto, WithdrawOutputDto)
from domain.models.account import Account
from domain.models.event import Event, DepositEvent, TransferEvent, WithdrawEvent
from domain.repositories.AccountRepository import AccountRepository
from domain.repositories.EventRepository import DepositEventRepository, TransferEventRepository, WithdrawEventRepository
from application.services.exceptions import AccountNotFoundException


class AccountsService:
    def __init__(self, account_repository: AccountRepository, deposit_event_repository: DepositEventRepository,
                 transfer_event_repository: TransferEventRepository, withdraw_event_repository: WithdrawEventRepository):
        self._account_repository = account_repository
        self._deposit_event_repository = deposit_event_repository
        self._transfer_event_repository = transfer_event_repository
        self._withdraw_event_repository = withdraw_event_repository

    def get_account_balance_by_id(self, account_id) -> AccountDto:
        account = self._account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundException(f"Account with id {account_id} not found.")
        return AccountDto(id=account_id, balance=account.balance)

    def list_accounts(self) -> List[Account]:
        return self._account_repository.list_accounts()

    def deposit(self, deposit_input_dto: DepositInputDto) -> DepositOutputDto:
        account = self._account_repository.get_account_by_id(deposit_input_dto.destination)
        if not account:
            account = self._create_account(deposit_input_dto.destination)
        deposit = DepositEvent(deposit_input_dto.destination, amount=deposit_input_dto.amount, created=datetime.now())
        self._deposit_event_repository.save(deposit)
        account.balance = self._get_account_balance(deposit_input_dto.destination)
        updated_account = self._account_repository.save(account)
        return DepositOutputDto(destination=AccountDto(id=account.id, balance=updated_account.balance))

    def empty_datasource(self) -> None:
        self._account_repository.reset()
        return None

    def transfer(self, transfer_input_dto: TransferInputDto) -> TransferOutputDto:
        origin = self._account_repository.get_account_by_id(transfer_input_dto.origin)
        destination = self._account_repository.get_account_by_id(transfer_input_dto.destination)
        if not origin:
            raise AccountNotFoundException("Account not found.")
        if not destination:
            destination = self._create_account(transfer_input_dto.destination)
        transfer = TransferEvent(destination=destination.id, origin=origin.id, amount=transfer_input_dto.amount, created=datetime.now())
        self._transfer_event_repository.save(transfer)
        origin.balance = self._get_account_balance(origin.id)
        updated_origin = self._account_repository.save(origin)
        origin_dto = AccountDto(id=origin.id, balance=updated_origin.balance)
        destination.balance = self._get_account_balance(destination.id)
        updated_destination = self._account_repository.save(destination)
        destination_dto = AccountDto(id=destination.id, balance=updated_destination.balance)
        return TransferOutputDto(origin=origin_dto, destination=destination_dto)

    def withdraw(self, withdraw_input_dto: WithdrawInputDto) -> WithdrawOutputDto:
        account = self._account_repository.get_account_by_id(withdraw_input_dto.origin)
        if not account:
            raise AccountNotFoundException("Account not found.")
        withdraw_event = WithdrawEvent(origin=account.id, amount=withdraw_input_dto.amount, created=datetime.now())
        self._withdraw_event_repository.save(withdraw_event)
        account.balance = self._get_account_balance(account.id)
        updated_account = self._account_repository.save(account)
        account_dto = AccountDto(id=account.id, balance=updated_account.balance)
        return WithdrawOutputDto(origin=account_dto)

    def _get_account_balance(self, account_id: str) -> int:
        events = self._get_account_extract(account_id)
        return sum([e.amount for e in events])

    def _get_account_extract(self, account_id: str) -> List[Event]:
        deposits = copy.deepcopy(self._deposit_event_repository.filter_by_destination_id(account_id))
        transfers_in = copy.deepcopy(self._transfer_event_repository.filter_by_destination_id(account_id))
        transfers_out = copy.deepcopy(self._transfer_event_repository.filter_by_origin_id(account_id))
        withdraws = copy.deepcopy(self._withdraw_event_repository.filter_by_origin_id(account_id))

        in_events_list = []
        in_events_list.extend(deposits)
        in_events_list.extend(transfers_in)
        in_dict = {}
        for element in in_events_list:
            in_dict[element.created] = element
        out_events_list = []
        out_events_list.extend(transfers_out)
        out_events_list.extend(withdraws)
        out_dict = {}
        for element in out_events_list:
            element.amount = -element.amount
            out_dict[element.created] = element

        ordered_event_list = []
        merged_dict = {}
        merged_dict.update(in_dict)
        merged_dict.update(out_dict)
        merged_sorted_dict = dict(sorted(merged_dict.items()))
        for value in merged_sorted_dict.values():
            ordered_event_list.append(value)

        return ordered_event_list

    def _create_account(self, account_id) -> Account:
        return self._account_repository.save(Account(id=account_id, balance=0))
