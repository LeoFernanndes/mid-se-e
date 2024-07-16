from pydantic import BaseModel


class AccountDto(BaseModel):
    id: str
    balance: int
