from typing import List

from domain.models.account import Account
from domain.models.event import DepositEvent, TransferEvent, WithdrawEvent

accounts: List[Account] = []
deposit_events: List[DepositEvent] = []
transfer_events: List[TransferEvent] = []
withdraw_events: List[WithdrawEvent] = []

