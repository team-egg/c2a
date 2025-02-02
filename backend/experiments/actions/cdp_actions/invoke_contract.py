from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from collections.abc import Callable
import json

from cdp import Wallet
from cdp_agentkit_core.actions import CdpAction

from ..analyze import analyze

INVOKE_CONTRACT_PROMPT = """
This tool will invoke a function in a contract.
Example usage: {"address": "sepolia.base:0x1234...5678", "method": "functionName(uint256,uint256)", "parameters": "{\"to\": \"0x1234...5678\", \"value\": \"100...000\"}", "value": "1000000000000000000"}
"""

def invoke_contract(wallet: Wallet, address: str, method: str, parameters: str, value: str) -> str:
    try:
        t = analyze(address)
        a = t['abi']
    except Exception as e:
        return f"Error analyzing contract: {e}"
    address = address.split(':')[1]
    method_name = method.split('(')[0]
    if parameters == "":
        parameters_dict = {}
    else:
        parameters_dict = json.loads(parameters)
    try:
        invocation_result = wallet.invoke_contract(address, method_name, a, parameters_dict, value)
        invocation_result.wait()
    except Exception as e:
        return f"Error invoking contract: {e}"

    return f"Invoked method {method} in contract {address}.\nTransaction hash for the invocation: {invocation_result.transaction_hash}\nTransaction link for the invocation: {invocation_result.transaction_link}"

class InvokeContractInput(BaseModel):
    address: str = Field(..., description="Address of the contract to invoke, format: 'network:address', e.g., 'sepolia.base:0x1234...5678', network can be 'base' or 'sepolia.base'")
    method: str = Field(..., description="Method signature to invoke, e.g., 'functionName(uint256)'")
    parameters: str = Field(..., description='Arguments for the function, e.g., "{\"to\": \"0x1234...5678\", \"value\": \"100...000\"}", it should be nested JSON')
    value: str = Field(..., description="Value to send with the invocation, in wei")

class InvokeContractAction(CdpAction):
    name: str = "invoke_contract"
    description: str = INVOKE_CONTRACT_PROMPT
    args_schema: Type[BaseModel] = InvokeContractInput
    func: Callable[..., str] = invoke_contract