from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from collections.abc import Callable
import json

from cdp import Cdp, Wallet, WalletData
from cdp_langchain.utils import CdpAgentkitWrapper
import os
import sys
import time

import actions.cdp_actions as _

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain.globals import set_verbose,set_debug

# Import CDP Agentkit Langchain Extension.
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper

wallet_data_file = "wallet_data.txt"
with open(wallet_data_file) as f:
    wallet_data = f.read()

# we don't need agentkit, but it's the simplest way to initialize CDP
agentkit = CdpAgentkitWrapper(cdp_wallet_data=wallet_data)

wallet = Wallet.import_data(WalletData.from_dict(json.loads(wallet_data)))
print(wallet)

contract_address = '0x19B57F2Ee33bcFDE75c1496B3752D099fc408Ef1'
method = 'approve'
abi = [{
    "constant": False,
    "inputs": [
        {
            "internalType": "address",
            "name": "spender",
            "type": "address"
        },
        {
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256"
        }
    ],
    "name": "approve",
    "outputs": [
        {
            "internalType": "bool",
            "name": "",
            "type": "bool"
        }
    ],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}]
parameters = {"spender": "0x19B57F2Ee33bcFDE75c1496B3752D099fc408Ef1", "amount": "1000000000000000000"}

invocation_result = wallet.invoke_contract(contract_address, method, abi, parameters, '0')
print(invocation_result)
print('Transaction hash:', invocation_result.transaction_hash)
time.sleep(3)
invocation_result.reload()
print(invocation_result)