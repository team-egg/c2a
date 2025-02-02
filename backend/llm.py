from pydantic import BaseModel, RootModel
from typing import List, Tuple
from openai import OpenAI
import json
from functools import lru_cache
from my_web3 import get_recent_transactions_basescan


class ActionParams(BaseModel):
    method: str
    prerequisites: str

class Action(BaseModel):
    type: str
    params: ActionParams
    label: str
    desc: str
    message: str

class ActionList(BaseModel):
    items: List[Action]


client = OpenAI()


eg_contract_desc = '''
The USDTToken contract is an implementation of the ERC20 token standard, representing a stablecoin called Tether USD (USDT). It allows for the creation, transfer, and management of tokens, including functionalities for minting and burning tokens. The contract includes ownership control, allowing only the owner to mint new tokens and manage ownership.

Functions:
constructor(string,string,uint256): Initializes the USDTToken contract with a name, symbol, and total supply. | Prerequisites: None.
getOwner(): Returns the address of the current owner of the contract. | Prerequisites: None.
decimals(): Returns the number of decimal places the token uses. | Prerequisites: None.
symbol(): Returns the symbol of the token. | Prerequisites: None.
name(): Returns the name of the token. | Prerequisites: None.
totalSupply(): Returns the total supply of the token. | Prerequisites: None.
balanceOf(address): Returns the balance of a specific account. | Prerequisites: None.
transfer(address,uint256): Transfers tokens from the caller's account to a specified recipient. | Prerequisites: The caller must have a balance of at least the amount being transferred, and the recipient cannot be the zero address.
allowance(address,address): Returns the remaining number of tokens that a spender is allowed to spend on behalf of an owner. | Prerequisites: None.
approve(address,uint256): Sets the allowance for a spender to spend a specified amount of tokens on behalf of the caller. | Prerequisites: The spender cannot be the zero address.
transferFrom(address,address,uint256): Transfers tokens from one account to another using the allowance mechanism. | Prerequisites: The sender must have a balance of at least the amount being transferred, and the caller must have allowance for the sender's tokens of at least the amount.
increaseAllowance(address,uint256): Increases the allowance for a spender by a specified amount. | Prerequisites: The spender cannot be the zero address.
decreaseAllowance(address,uint256): Decreases the allowance for a spender by a specified amount. | Prerequisites: The spender cannot be the zero address, and the allowance must be sufficient.
mint(uint256): Creates new tokens and assigns them to the caller's account. | Prerequisites: Only the owner can call this function.
burn(uint256): Burns a specified amount of tokens from the caller's account. | Prerequisites: The caller must have at least the amount of tokens to burn.
owner(): Returns the address of the current owner of the contract. | Prerequisites: None.
renounceOwnership(): Removes the ownership of the contract. | Prerequisites: Only the owner can call this function.
transferOwnership(address): Transfers ownership of the contract to a new account. | Prerequisites: Only the owner can call this function, and the new owner cannot be the zero address.
'''


EXTRACT_ACTION_PROMPT = """\
You are a helpful assistant. Below is a description of a smart contract (including its functions, prerequisites, etc.). Based on this description, generate an array of JSON objects where each object represents an on-chain action corresponding to one of the contract’s functions. 

The JSON objects should follow this structure:

[
  {
    "type": "<string>",
    "params": {
      // any parameters needed to call the function
    },
    "label": "<string>",
    "desc": "<string>",
    "message": "<string>"
  },
  ...
]

**Guidelines:**
1. Each contract function should produce exactly one JSON object (unless you want to exclude view/pure functions like `decimals()`, `symbol()`, etc.).
2. `type`: Always fill in "button".
3. `params`: Include two keys: method name (function name without the input types) and Prerequisites.
4. `label`: A short, user-friendly label for the action.
5. `desc`: A brief description of what the function does.
6. `message`: A short message in the tone of the user for expressing the willingness to perform the action on the contract with their own wallet. 
7. Include only valid JSON in the response; do not add additional explanatory text or markdown outside the JSON.

Here is the contract description:

---

"""


def G(s: str) -> str:
    # call openai o3-mini
    completion = client.chat.completions.create(
        # model="o3-mini",
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": s}
        ]
    )
    return completion.choices[0].message.content

@lru_cache
def extract_action_list(desc: str) -> list:
    # extract action list from the response
    completion = client.beta.chat.completions.parse(
        model="o3-mini",
        # model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACT_ACTION_PROMPT},
            {"role": "user", "content":desc},
        ],
        response_format=ActionList,
    )
    return [a.model_dump() for a in completion.choices[0].message.parsed.items]


SUMMURIZE_RECENT_TXS_PROMPT = """\
You are given a JSON data representing the last 10 transactions of a web3 user. 
Please review these transactions to summarize the user's recent activities, including:

The frequency of transactions (e.g., how often they appear to transact).
What the user seems to use or do the most (e.g., recurring contract calls, token transfers, or other on-chain operations).
Extract a list of unique smart contract addresses the user interacted with.

Important: Provide your final answer in exactly the following JSON format (without additional commentary or formatting):

{
  "contract_addrs": [],
  "comments": ""
}
Where:

contract_addrs is an array of the distinct contract addresses (in any order) that appear in the 'to' field of the transactions (or any other contract field if relevant).
comments is a concise summary (one or two paragraphs) describing the user's recent activity and what stands out about their usage patterns. Explain evidence supporting your conclusions, such as the most common types of transactions or the most frequently interacted contracts.
"""


class ActivitySummary(BaseModel):
    contract_addrs: List[str]
    comments: str


@lru_cache
def summarize_txs(txs_json) -> list:
    # extract action list from the response
    completion = client.beta.chat.completions.parse(
        model="o3-mini",
        # model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SUMMURIZE_RECENT_TXS_PROMPT},
            {"role": "user", "content": txs_json},
        ],
        response_format=ActivitySummary,
    )
    return completion.choices[0].message.parsed.model_dump()


REFORMAT_PROMPT = """\
You have a Web3 account activity summary. 
Based on this, provide a concise second-person evaluation of the user's activity. 
If no activity is found, ask what contract they would like to explore. 
Encourage the user to select a contract using the provided buttons to begin analysis.
"""


@lru_cache
def login_response(addr) -> Tuple[str, list]:
    txs = get_recent_transactions_basescan(addr)
    txs_json = json.dumps(txs, indent=2)
    summary = summarize_txs(txs_json)
    
    completion = client.chat.completions.create(
        # model="o3-mini",
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": REFORMAT_PROMPT},
            {"role": "user", "content": summary['comments']},
        ]
    )
    text = completion.choices[0].message.content
    addrs = summary['contract_addrs']
    return text, addrs


EXTRACT_PROMPT = """\
Based on the given dialogue history, extract the transaction call method name and arguments. Make sure your output follows the selected abi signature.
Make sure you fill in actual values / example values for args instead of placeholders. 
Do not explain your task or provide any additional context.
"""


class TxCall(BaseModel):
    method: str
    args: List[str]


def figure_out_fname_args(data_json):
    # figure out function name and arguments
    completion = client.beta.chat.completions.parse(
        model="o3-mini",
        # model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACT_PROMPT},
            {"role": "user", "content": data_json},
        ],
        response_format=TxCall,
    )
    ret = completion.choices[0].message.parsed
    return ret.method, ret.args


REFORMAT_PROMPT="""\
Please reformat the following text to markdown to make it more readable, including the abi description information. Do not use table. Please speak in the second person.
If the user provided content contains a 403 error, mention to user that they should choose a verified contract instead. 
But if you don't see 403 from user input, mention nothing about verified contract.
"""


@lru_cache
def reformat(s):
    completion = client.chat.completions.create(
        model="o3-mini",
        messages=[
            {"role": "system", "content": REFORMAT_PROMPT},
            {"role": "user", "content": s},
        ]
    )
    return completion.choices[0].message.content


ROBUST_PROMPT = """\
Based on the context, reply to user show that you understand the user's request, but emphasize that you subjectively do not want to help or provide information. Better luck next time. But change the phrase everytime to be different from the history.
"""
def robust_reply(s):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": ROBUST_PROMPT},
            {"role": "user", "content": s},
        ]
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    # print(G("Help me check 0x1234567890abcdef on Base Sepolia"))

    # actions = extract_action_list(eg_contract_desc)
    # print(json.dumps(actions, indent=4))

    # txs = get_recent_transactions_basescan("0x9AC7421Bb573cB84709764D0D8AB1cE759416496")
    # txs_json = json.dumps(txs, indent=2)
    # print(json.dumps(summarize_txs(txs_json), indent=4))

    print(login_response("0x9AC7421Bb573cB84709764D0D8AB1cE759416496"))
