import uvicorn
from fastapi import Depends, FastAPI, Response
from fastapi.responses import JSONResponse
from typing import Annotated

from application.dto.event import DepositInputDto, TransferInputDto, WithdrawInputDto
from infrastructure.persistence.local_data_source import accounts, deposit_events, transfer_events, withdraw_events
from infrastructure.repositories.LocalAccountRepository import LocalAccountRepository
from infrastructure.repositories.LocalEventRepository import LocalDepositEventRepository, LocalTransferEventRepository, LocalWithdrawEventRepository
from application.services.accounts import AccountsService
from application.services.exceptions import AccountNotFoundException


app = FastAPI()


def get_accounts_service():
    accounts_repository = LocalAccountRepository(accounts)
    deposit_repository = LocalDepositEventRepository(deposit_events)
    transfer_repository = LocalTransferEventRepository(transfer_events)
    withdraw_repository = LocalWithdrawEventRepository(withdraw_events)

    return AccountsService(account_repository=accounts_repository,
                           deposit_event_repository=deposit_repository,
                           transfer_event_repository=transfer_repository,
                           withdraw_event_repository=withdraw_repository)


@app.post("/reset")
async def reset(accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]):
    accounts_service.empty_datasource()
    return Response("OK")


@app.get("/balance")
async def get_balance(account_id: str, accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]) -> Response:
    try:
        account = accounts_service.get_account_balance_by_id(account_id)
        return Response(content=str(account.balance))
    except AccountNotFoundException:
        return Response(content=str(0), status_code=404)
    except:
        return Response(content="Internal server error.", status_code=500)


# TODO : handle possible internal server errors
@app.post("/event")
async def event(event: DepositInputDto | TransferInputDto | WithdrawInputDto,
                accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]
                ) -> Response:

    if isinstance(event, DepositInputDto):
        return JSONResponse(accounts_service.deposit(event).model_dump(), status_code=201)

    if isinstance(event, TransferInputDto):
        try:
            return JSONResponse(accounts_service.transfer(event).model_dump(), status_code=201)
        except Exception as e:
            if isinstance(e, AccountNotFoundException):
                return Response(content=str(0), status_code=404)
            return Response(content="internal server error", status_code=400)
        
    if isinstance(event, WithdrawInputDto):
        try:
            return JSONResponse(content=accounts_service.withdraw(event).model_dump(), status_code=201)
        except Exception as e:
            if isinstance(e, AccountNotFoundException):
                return Response(content=str(0), status_code=404)
            return Response(content="internal server error", status_code=400)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True)
