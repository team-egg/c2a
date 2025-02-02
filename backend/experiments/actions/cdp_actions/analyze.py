from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from collections.abc import Callable

from functools import lru_cache

from cdp_agentkit_core.actions import CdpAction

from ..analyze import analyze

ANALYZE_CONTRACT_PROMPT = """
This tool will analyze the contract at the given address.
A summary of the contract and functions will be returned.
"""


@lru_cache
def analyze_contract(address: str) -> str:
    address = address.lower()
    if '..' in address or '/' in address:
        return 'Malformed address'
    #if not address.startswith('0x'):
    #    return 'Malformed address'
    #if not all(x in '0123456789abcdef' for x in address[2:]):
    #    return 'Malformed address'
    try:
        t = analyze(address)
        s = t['analysis']
    except Exception as e:
        # print stack
        import traceback
        traceback.print_exc()
        return f"Error analyzing contract: {e}"
    a = s['description']
    a += f"\n\nFunctions:"
    for name, f in s['functions'].items():
        a += f"\n{name}: {f['description']} | Prerequisites: {f['prerequisites']}"
    return a

class AnalyzeContractInput(BaseModel):
    address: str = Field(..., description="Address of the contract to analyze, format: 'network:address', e.g., 'sepolia.base:0x1234...5678', network can be 'base' or 'sepolia.base'")

class AnalyzeContractAction(CdpAction):
    name: str = "analyze_contract"
    description: str = ANALYZE_CONTRACT_PROMPT
    args_schema: type[BaseModel] | None = AnalyzeContractInput
    func: Callable[..., str] = analyze_contract

GET_CONTRACT_FUNCTION_DETAILS_PROMPT = """
This tool will get the details of a function in a contract, including the function signature, description, parameters, and prerequisites.
"""

def get_contract_function_details(address: str, function_signature: str) -> str:
    try:
        t = analyze(address)
        s = t['analysis']
        a = t['abi']
    except Exception as e:
        return f"Error analyzing contract: {e}"
    function_name = function_signature.split('(')[0]
    for abi in a:
        if abi['type'] == 'function':
            if abi['name'] == function_name:
                break
    f = s['functions'][function_signature]
    if f is None:
        return f"Function {function_signature} not found in contract {address}"
    res = f"Function {function_signature} details:\n"
    res += f"Raw ABI: {str(abi)}\n"
    res += f"Detailed Description: {f['detail']}\n"
    for i, x in enumerate(f['parameters']):
        res += f"Parameter {i}: {x}\n"
    res += f"Prerequisites: {f['prerequisites']}"
    return res 

class GetContractFunctionDetailsInput(BaseModel):
    address: str = Field(..., description="Address of the contract to analyze, format: 'network:address', e.g., 'sepolia.base:0x1234...5678', network can be 'base' or 'sepolia.base'")
    function_signature: str = Field(..., description="Signature of the function to get details for, e.g., 'functionName(uint256)'")

class GetContractFunctionDetailsAction(CdpAction):
    name: str = "get_contract_function_details"
    description: str = GET_CONTRACT_FUNCTION_DETAILS_PROMPT
    args_schema: type[BaseModel] | None = GetContractFunctionDetailsInput
    func: Callable[..., str] = get_contract_function_details
