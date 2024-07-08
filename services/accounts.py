from typing import List

from dto.account import AccountDto
from dto.event import DepositInputDto, DepositOutputDto, TransferInputDto, TransferOutputDto, WithdrawInputDto, WithdrawOutputDto
from models.account import Account
from repositories.AccountRepository import AccountRepository
from services.exceptions import AccountNotFoundException


class AccountsService:
    def __init__(self, account_repository: AccountRepository):
        self._account_repository = account_repository

    def get_account_by_id(self, id: str) -> Account | None:
        return self._account_repository.get_account_by_id(id)

    def list_accounts(self) -> List[Account]:
        return self._account_repository.list_accounts()

    def deposit(self, deposit_input_dto: DepositInputDto) -> DepositOutputDto:
        account = self._account_repository.get_account_by_id(deposit_input_dto.destination)
        if not account:
            new_account_payload = Account(id=deposit_input_dto.destination, balance=deposit_input_dto.amount)
            new_account = self._account_repository.save(new_account_payload)
            acount_dto = AccountDto(id=new_account.id, balance=new_account.balance)
            return DepositOutputDto(destination=acount_dto)
        else:
            account.balance += deposit_input_dto.amount
            updated_account = self._account_repository.save(account)
            acount_dto = AccountDto(id=updated_account.id, balance=updated_account.balance)
            return DepositOutputDto(destination=acount_dto)

    def empty_datasource(self) -> None:
        self._account_repository.reset()
        return None

    def transfer(self, transfer_input_dto: TransferInputDto) -> TransferOutputDto:
        origin = self._account_repository.get_account_by_id(transfer_input_dto.origin)
        destination = self._account_repository.get_account_by_id(transfer_input_dto.destination)
        if not origin:
            raise AccountNotFoundException("Account not found.")
        if not destination:
            deposit_input_dto = DepositInputDto(type="deposit", destination=transfer_input_dto.destination, amount=0)
            self.deposit(deposit_input_dto)
            destination = self._account_repository.get_account_by_id(transfer_input_dto.destination)
        origin.balance -= transfer_input_dto.amount
        updated_origin = self._account_repository.save(origin)
        destination.balance += transfer_input_dto.amount
        updated_destination = self._account_repository.save(destination)
        origin_dto = AccountDto(id=updated_origin.id, balance=updated_origin.balance)
        destination_dto = AccountDto(id=updated_destination.id, balance=updated_destination.balance)
        return TransferOutputDto(origin=origin_dto, destination=destination_dto)

    def withdraw(self, withdraw_input_dto: WithdrawInputDto) -> WithdrawOutputDto:
        account = self._account_repository.get_account_by_id(withdraw_input_dto.origin)
        if not account:
            raise AccountNotFoundException("Account not found.")
        new_balance = account.balance - withdraw_input_dto.amount
        account.balance = new_balance
        updated_account = self._account_repository.save(account)
        account_dto = AccountDto(id=updated_account.id, balance=updated_account.balance)
        return WithdrawOutputDto(origin=account_dto)
