from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Union

from application.dto.account import AccountDto


class DepositInputDto(BaseModel):
    type: Literal["deposit"]
    destination: str
    amount: int


class DepositOutputDto(BaseModel):
    destination: AccountDto


class TransferInputDto(BaseModel):
    type: Literal["transfer"]
    origin: str
    amount: int
    destination: str


class TransferOutputDto(BaseModel):
    origin: AccountDto
    destination: AccountDto


class WithdrawInputDto(BaseModel):
    type: Literal["withdraw"]
    origin: str
    amount: int


class WithdrawOutputDto(BaseModel):
    origin: AccountDto


class EventOutputDto(BaseModel):
    created: datetime
    event: Union[DepositInputDto, TransferInputDto, WithdrawInputDto]
