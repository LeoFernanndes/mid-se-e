from typing import List, Union

from application.dto.account import AccountDto
from application.dto.event import (EventOutputDto, DepositInputDto, DepositOutputDto, TransferInputDto, TransferOutputDto,
                                   WithdrawInputDto, WithdrawOutputDto)
from domain.models.account import Account
from domain.models.event import DepositEvent, TransferEvent, WithdrawEvent
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
        deposit = DepositEvent(deposit_input_dto.destination, amount=deposit_input_dto.amount)
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
        transfer = TransferEvent(destination=destination.id, origin=origin.id, amount=transfer_input_dto.amount)
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
        withdraw_event = WithdrawEvent(origin=account.id, amount=withdraw_input_dto.amount)
        self._withdraw_event_repository.save(withdraw_event)
        account.balance = self._get_account_balance(account.id)
        updated_account = self._account_repository.save(account)
        account_dto = AccountDto(id=account.id, balance=updated_account.balance)
        return WithdrawOutputDto(origin=account_dto)

    def _get_account_balance(self, account_id: str) -> int:
        deposits = self._deposit_event_repository.filter_by_destination_id(account_id)
        sum_deposits = sum([d.amount for d in deposits])
        transfers_in = self._transfer_event_repository.filter_by_destination_id(account_id)
        sum_transfers_in = sum([t.amount for t in transfers_in])
        transfers_out = self._transfer_event_repository.filter_by_origin_id(account_id)
        sum_transfers_out = sum([t.amount for t in transfers_out])
        withdraws = self._withdraw_event_repository.filter_by_origin_id(account_id)
        sum_withdraws = sum([w.amount for w in withdraws])
        return sum_deposits + sum_transfers_in - sum_transfers_out - sum_withdraws

    def _create_account(self, account_id) -> Account:
        return self._account_repository.save(Account(id=account_id, balance=0))
