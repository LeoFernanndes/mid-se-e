from abc import ABC, abstractmethod
from typing import List

from models.account import Account


class AccountRepository(ABC):

    @abstractmethod
    def get_account_by_id(self, id: str) -> Account | None:
        pass

    @abstractmethod
    def list_accounts(self) -> List[Account]:
        pass

    @abstractmethod
    def save(self, account: Account) -> Account:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass
