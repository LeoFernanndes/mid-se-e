import random
from typing import List

from domain.repositories.AccountRepository import AccountRepository
from domain.models.account import Account


class LocalAccountRepository(AccountRepository):
    def __init__(self, data_source: List[Account]):
        self._data_source = data_source

    def get_account_by_id(self, id: str) -> Account | None:
        account = list(filter(lambda x: x.id == id, self._data_source))
        if account and len(account):
            return account[0]
        else:
            return None

    def list_accounts(self) -> List[Account]:
        return self._data_source

    def save(self, account: Account) -> Account:
        if account.id is None:
            account_ids = [account.id for account in self._data_source]
            for i in range(1000):
                _id = str(self._generate_random_id())
                if _id not in account_ids:
                    account.id = _id
                    self._data_source.append(account)
                break
            return account

        old_account = self.get_account_by_id(account.id)
        if old_account:
            for _account in self._data_source:
                if account.id == _account.id:
                    _account = account
                break
            return self.get_account_by_id(old_account.id)

        else:
            self._data_source.append(account)
            return account

    def reset(self) -> None:
        self._data_source.clear()
        return None

    def _generate_random_id(self):
        return random.randint(1, 1000000)
