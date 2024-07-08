import uvicorn
from fastapi import Depends, FastAPI, Response
from fastapi.responses import JSONResponse
from typing import List, Annotated, Union

from dto.account import AccountDto
from dto.event import DepositInputDto, DepositOutputDto, TransferInputDto, TransferOutputDto, WithdrawInputDto, WithdrawOutputDto
from local_data_source import accounts
from repositories.LocalAccountRepository import LocalAccountRepository
from services.accounts import AccountsService
from services.exceptions import AccountNotFoundException


app = FastAPI()


def get_accounts_service():
    accounts_data_source = accounts
    accounts_repository = LocalAccountRepository(accounts_data_source)
    return AccountsService(accounts_repository)


@app.post("/reset")
async def reset(accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]):
    accounts_service.empty_datasource()
    return Response("OK")


@app.get("/balance")
async def get_balance(account_id: str, accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]) -> Response:
    account = accounts_service.get_account_by_id(account_id)
    if not account:
        return Response(content=str(0), status_code=404)
    return Response(content=str(account.balance))


# TODO : handle possible internal server errors
@app.post("/event")
async def event(event: DepositInputDto | TransferInputDto | WithdrawInputDto,
                accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]
                ) -> Response:

    if isinstance(event, DepositInputDto):
        return JSONResponse(accounts_service.deposit(event).dict(), status_code=201)

    if isinstance(event, TransferInputDto):
        try:
            return JSONResponse(accounts_service.transference(event).dict(), status_code=201)
        except Exception as e:
            if isinstance(e, AccountNotFoundException):
                return Response(content=str(0), status_code=404)
            return Response(content="internal server error", status_code=400)

    elif isinstance(event, WithdrawInputDto):
        try:
            return JSONResponse(content=accounts_service.withdraw(event).dict(), status_code=201)
        except Exception as e:
            if isinstance(e, AccountNotFoundException):
                return Response(content=str(0), status_code=404)
            return Response(content="internal server error", status_code=400)


@app.get("/accounts")
async def list_accounts(accounts_service: Annotated[AccountsService, Depends(get_accounts_service)]) -> List[AccountDto]:
    _accounts = accounts_service.list_accounts()
    return [AccountDto(**account.__dict__) for account in _accounts]


# TODO: Apply the following schema definitions to the event case
@app.get("/schema/", response_model=Union[DepositOutputDto, TransferOutputDto, WithdrawOutputDto], responses={
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "examples": {
                    "transfer": {
                        "summary": "Transfer Response",
                        "value": {"origin": {"id": 1, "balance": 10}, "destination": {"id": 2, "balance": 20}}
                    },
                    "withdraw ": {
                        "summary": "Withdraw Response",
                        "value": {"origin": {"id": 1, "balance": 15}}
                    }
                }
            }
        }
    }
})
async def schema():
    return "ok"


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info", reload=True)
