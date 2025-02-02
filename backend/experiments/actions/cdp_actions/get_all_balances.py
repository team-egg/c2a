from collections.abc import Callable

from cdp import Wallet, Address
from pydantic import BaseModel, Field

from cdp_agentkit_core.actions import CdpAction

GET_ALL_BALANCES_PROMPT = """
This tool will get the balance of all tokens and ETH in the wallet.
The balances will be returned as a JSON encoded string.

It takes the following inputs:
- address: (Optional) The address to check balance for. If not provided, uses the wallet's default address
"""


class GetAllBalancesInput(BaseModel):
    address: str | None = Field(
        None,
        description="The address to check balance for. If not provided, uses the wallet's default address",
    )


def get_all_balances(wallet: Wallet, address: str | None = None) -> str:
    check_address = address if address is not None else wallet.default_address.address_id
    address_obj = Address(wallet.network_id, check_address)
    balances = address_obj.balances()
    if address is None:
        return f"Balances for default wallet:\n{str(balances)}"
    return f"Balances for address {check_address}:\n{str(balances)}"


class GetAllBalanceAction(CdpAction):
    name: str = "get_all_balances"
    description: str = GET_ALL_BALANCES_PROMPT
    args_schema: type[BaseModel] | None = GetAllBalancesInput
    func: Callable[..., str] = get_all_balances
