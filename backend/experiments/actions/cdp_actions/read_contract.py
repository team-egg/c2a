from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from collections.abc import Callable
import json

from cdp import Wallet
from cdp_agentkit_core.actions import CdpAction
from web3 import Web3

from ..analyze import analyze

READ_CONTRACT_PROMPT = """
This tool will call a readonly function in a contract.
Example usage: {"address": "sepolia.base:0x1234...5678", "method": "functionName(uint256,uint256)", "parameters": "{\"to\": \"0x1234...5678\", \"value\": \"100...000\"}"}
"""

web3s = {
    "base": Web3(Web3.HTTPProvider("https://mainnet.base.org")),
    "sepolia.base": Web3(Web3.HTTPProvider("https://sepolia.base.org")),
}

def read_contract(address: str, method: str, parameters: str) -> str:
    try:
        t = analyze(address)
        a = t['abi']
    except Exception as e:
        return f"Error analyzing contract: {e}"
    network, address = address.split(':')
    web3 = web3s[network]
    method_name = method.split('(')[0]
    if parameters == "":
        parameters_dict = {}
    else:
        parameters_dict = json.loads(parameters)
    try:
        contract = web3.eth.contract(address=address, abi=a)
        result = contract.functions[method_name](**parameters_dict).call()
    except Exception as e:
        return f"Error calling contract: {e}"
    return f"Called method {method} in contract {address}.\nResult: {result}"

class ReadContractInput(BaseModel):
    address: str = Field(..., description="Address of the contract to invoke, format: 'network:address', e.g., 'sepolia.base:0x1234...5678', network can be 'base' or 'sepolia.base'")
    method: str = Field(..., description="Method signature to invoke, e.g., 'functionName(uint256)'")
    parameters: str = Field(..., description='Arguments for the function, e.g., "{\"to\": \"0x1234...5678\", \"value\": \"100...000\"}", it should be nested JSON')

class ReadContractAction(CdpAction):
    name: str = "read_contract"
    description: str = READ_CONTRACT_PROMPT
    args_schema: Type[BaseModel] = ReadContractInput
    func: Callable[..., str] = read_contract