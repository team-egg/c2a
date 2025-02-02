from flask import Flask, request, Response, g
import os
import json
import time
import requests
from flask_cors import CORS
from llm import G, extract_action_list, figure_out_fname_args, reformat, robust_reply


# add "./experiments" to python path
import sys
sys.path.append("./experiments")


from experiments import analyze_contract, generate_cdp_action

from cdp import Cdp, Wallet, WalletData
Cdp.configure(
    "organizations/ad5564a0-9012-400b-ae9b-0843e084fc18/apiKeys/2011b944-729e-4312-af52-0efd2cf9a2f4",
    "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIOn1G6f9LFP5Jwla1lh90K6370L9MvUkylZSESs0aGYBoAoGCCqGSM49\nAwEHoUQDQgAEJyGRDOootBfxy3RISUMdJYo92GTg34dN2CXK3zjK+kOagk0SQqtx\nA4a1pwhIbPfq/46h/gsJx/zVsbbgFP4v7A==\n-----END EC PRIVATE KEY-----\n",
    source="cdp-langchain", # if we don't set this, the faucet will not work
    source_version="0.0.13",
)


# download from https://gist.githubusercontent.com/veox/8800debbf56e24718f9f483e1e40c35c/raw/f853187315486225002ba56e5283c1dba0556e6f/erc20.abi.json
ERC20_ABI = requests.get("https://gist.githubusercontent.com/veox/8800debbf56e24718f9f483e1e40c35c/raw/f853187315486225002ba56e5283c1dba0556e6f/erc20.abi.json").json()
TEST_MARKDOWN_CONTENT = """
# Test Markdown

- Bullet point 1
- Bullet point 2

## Subheading

1. Numbered list item 1
2. Numbered list item 2

**Bold text**

*Italic text*

> Blockquote

Table:

| Header 1 | Header 2 |
|----------|----------|
| Row 1    | Row 1    |
| Row 2    | Row 2    |

`Inline code`

block

```python
def test_code_block():
    return "Code block"
```

separator

above
---
below
---
again below

"""


app = Flask(__name__)
# CORS(app)


def W(s="", end=False):  # SSE wrapper
    if end:
        return "data: [DONE]\n\n"
    # return "data: " + s + "\n\n"
    return "data: " + (json.dumps(s) if s!="@@@" else s) + "\n\n"


def simulated_stream(s):  # FIXME: connect to streamed version of openai later
    words = s.split(" ")
    for word in words:
        # Simulate processing time
        time.sleep(0.01)
        # Yield each word followed by a space
        yield W(word + " ")


def generate_init_response():
    response_text = f"Hi, I'm C-2AO, your personal Web3 expert! How can I help you today?"
    
    yield from simulated_stream(response_text)
    yield W("@@@")
    metadata = {
        "actionList": [
            {
                "type": "button",
                "params": {},
                "label": "Explore",
                "desc": "Explore what others are doing on-chain",
                "message": "I want to see what others are doing with C-2AO."
            },
            {
                "type": "button_ask_contract",
                "params": {},
                "label": "Contract-to-Action",
                "desc": "Convert a smart contract into an agentic action",
                "message": "Help me check <contract_address> on <network_id>."
            },
            {
                "type": "button_login",
                "params": {},
                "label": "Login & Guess why I'm here",
                "desc": "Login to help agent understand how it can help you",
            },
        ]
    }
    yield W(metadata)
    yield W(end=True)


def try_get_user_address(data):
    if "user_address" in data:
        return data["user_address"]
    history = data['history']
    for m in history:
        if m['role'] == 'user' and 'address' in m:
            return m['address']
    return None


def try_get_contract_and_network(data):
    history = data['history']
    contract_address = None
    network_id = None
    for m in reversed(history):
        if 'message' in m and "Help me check" in m['message']:
            contract_address = [s for s in m['message'].split() if s.startswith('0x')][0]
            network_id = m['message'].split(" on ")[1].split(".")[0]
            if network_id == "Base Sepolia":
                network_id = "sepolia.base"
            break
    return contract_address, network_id


def c2a(data):
    history = data['history']
    # extract contract address & network
    contract_address, network_id = try_get_contract_and_network(data)
    
    yield from simulated_stream("Analyzing contract...\n")
    s = analyze_contract(f"{network_id}:{contract_address}")
    # yield from simulated_stream("Analyzing contract...\n")
    # yield from simulated_stream(s)
    yield from simulated_stream(reformat(s))
    yield from simulated_stream("\n\n\n\nPlease see the potential action list below. \n(It might take a while for the first run.)\n")
    yield from simulated_stream("Generating...")
    eal = extract_action_list(s)
    yield from simulated_stream("Done.\n")
    yield W("@@@")
    yield W({"actionList": eal})
    # yield W({"actionList": [
    #         {
    #             "type": "group",
    #             "children": [
    #                 extract_action_list(s)
    #             ]
    #         },
    # ]})

    yield W(end=True)
    return

def selected_contract_action(data):  # the user selected an action that bot provided in the previous message
    history = data['history']
    if len(history) < 4:
        return None
    last_bot_msg = history[-2]
    last_usr_msg = history[-1]
    if last_bot_msg['role'] != 'bot' or last_usr_msg['role'] != 'user':
        return None
    if 'actionList' not in last_bot_msg:
        return None
    if "Please see the potential action list below." not in last_bot_msg['message']:
        return None
    for action in last_bot_msg['actionList']:
        if action['label'] == last_usr_msg['label'] and action['message'] == last_usr_msg['message']:
            return action
    return None


def get_prev_action(history):
    if len(history) <= 1:
        return {"actionList": []}
    return {"actionList": history[-2]['actionList']}


def should_prepare_tx(data):
    history = data['history']
    if len(history) < 4:
        return False
    last_bot_msg = history[-2]
    last_usr_msg = history[-1]
    if "Prepare the transaction for me." in last_usr_msg['message']:
        return True


def prepare_tx(data):
    yield from simulated_stream("Preparing transaction...\n")
    # I need: 
    # - wallet context
    # - contract address
    # - method
    # To generate
    # - parameters
                # "address": '0xdd20cC951372F4a82E9Ba429F805084180C20643',
                # "abi": ERC20_ABI,
                # "functionName": 'transfer',
                # "args": ['0xF0110D0fa36101990C12B65e292940dC4B8D2b82', 1000000000000000000],
    contract_address = try_get_contract_and_network(data)[0]
    # endpoint:   
    # https://api.basescan.org/api
    #    ?module=contract
    #    &action=getabi
    #    &address=0xe1621db14277d66c356e14888c57ef1c0c0dc195
    #    &apikey=YourApiKeyToken
    abi = requests.get("https://api.etherscan.io/v2/api", params={
        "chainid": "84532",
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": "PTEBWYKR82V43W19RIV2W6WMMR8Z8TNIVQ",
    }).json()["result"]
    fname, args = figure_out_fname_args(json.dumps(data, indent=2))
    params = {
                    "chainId": 84532,
                    "address": contract_address,
                    "abi": json.loads(abi),
                    "functionName": fname,
                    "args": args,
                }
    yield from simulated_stream(f"Transaction prepared. Here is the transaction details:\n```json\n{json.dumps({'address': contract_address,'functionName': fname,'args': args}, indent=4)}\n```\n")
    metadata = {
        "actionList": [
            {
                "type": "invoke_tx",
                "params": params,
                "label": "Invoke Tx",
                "desc": "Invoke wallet to sign the transaction",
                "message": "I just sent the transaction."
            },
            {
                "type": "button",
                "params": {},
                "label": "Skip, Unlock Agent Wallet",
                "desc": "Skip the transaction and unlock agent wallet",
                "message": "Skip, Unlock Agent Wallet"
            }
        ],
    }
    yield W("@@@")
    yield W(metadata)
    yield W(end=True)


def agent_task(data):
    yield from simulated_stream("Congrats on finished transaction!\n")
    yield from simulated_stream("Now you can ask the C-2AO agent to run transactions with its own wallet. The First step is to unlock an agent wallet.\n")
    yield W("@@@")
    metadata = {
        "actionList": [
            {
                "type": "button",
                "params": {},
                "label": "Unlock",
                "desc": "Unlock agent wallet",
                "message": "Unlock agent wallet"
            },
        ]
    }
    yield W(metadata)
    yield W(end=True)


def get_agent_wallet(user_address):
    '''
    if os.path.exists(f'agent_wallets/{user_address}'):
        wallet_data = open(f'agent_wallets/{user_address}').read()
        wallet = Wallet.import_data(WalletData.from_dict(json.loads(wallet_data)))
    else:
        wallet = Wallet.create(network_id='base-sepolia')
        tx = wallet.faucet()
        tx.wait()
        wallet_data_dict = wallet.export_data().to_dict()
        wallet_data_dict["default_address_id"] = wallet.default_address.address_id
        open(f'agent_wallets/{user_address}', 'w').write(json.dumps(wallet_data))
    '''
    wallet_data = {
        "wallet_id": "cb9a7ab6-ac01-4637-bb7a-bc1fb844b566",
        "seed": "1d45f6fb8b26ffe70ffe1be5d72bee6db9420d5f8ce713b5ae5956ca5c95642389d72e44365307951c0b59c8cb24f403517f8a378934a1e2c61663f0c7f3050e",
        "network_id": "base-sepolia",
        "default_address_id": "0x54894d4F000032D85DAb39cE2041a2B1B86a022C"
    }
    wallet = Wallet.import_data(WalletData.from_dict(wallet_data))
    return wallet


def generate_response(data):
    """Generate a streaming response word by word"""

    history = data['history']

    if not history:
        # Return a welcome message
        yield from generate_init_response()
    else:
        # sanity check that the last message was from the user
        last_message = history[-1]
        if last_message['role'] != 'user':
            yield from simulated_stream("Err (last message was not from user)")
            yield W("@@@")
            yield W({"actionList": []})
            yield W(end=True)
            return
        
        # Temp: for debug transaction
        if last_message["message"].upper().strip() == "TEST TX":
            address = try_get_user_address(data)
            if not address:
                yield from simulated_stream("Please login / provide your address first.")
                yield W("@@@")
                yield W({"actionList": []})
                yield W(end=True)
                return
            yield from simulated_stream("Testing transaction... (check the action)")
            params = {
                "address": '0xdd20cC951372F4a82E9Ba429F805084180C20643',
                "abi": ERC20_ABI,
                "chainId": 84532,
"functionName": 'transfer',
                "args": ['0xF0110D0fa36101990C12B65e292940dC4B8D2b82', 1000000000000000000],
            }
            filtered_params = {
                "address": '0xdd20cC951372F4a82E9Ba429F805084180C20643',
                "chainId": 84532,
                "abi": [i for i in ERC20_ABI if i.get('name', '').lower() == 'transfer'][0],
                "functionName": 'transfer',
                "args": ['0xF0110D0fa36101990C12B65e292940dC4B8D2b82', 1000000000000000000],
            }
            # show tx
            yield from simulated_stream(f'\n\n```json\n{json.dumps({"from": address,"params": filtered_params}, indent=4)}\n```\n')
            metadata = {
                "actionList": [
                    {
                        "type": "invoke_tx",
                        "params": params,
                        "label": "Invoke Tx",
                        "desc": "Run the text transaction",
                        "message": "I'm sending the test transaction. <tx_id>"
                    }
                ],
            }
            yield W("@@@")
            yield W(metadata)
            yield W(end=True)
            return
        elif last_message["message"].upper().strip() == "TEST MD":
            yield from simulated_stream(TEST_MARKDOWN_CONTENT)
            yield W("@@@")
            metadata = {
                "actionList": []
            }
            yield W(metadata)
            yield W(end=True)
            return
        elif last_message["message"].upper().strip() == "TEST DL":
            yield from simulated_stream("test download...")
            yield W("@@@")
            metadata = {
                "actionList": [
                    {
                        "type": "download",
                        "params": {
                            "content": open("llm.py").read(),
                            "filename": "action.py"
                        },
                        "label": "Download",
                        "desc": "Download a file",
                        "message": "<Err> THIS SHOULD NOT BE DISPLAYED"
                    }
                ]
            }
            yield W(metadata)
            yield W(end=True)
            return
        elif last_message["message"].upper().strip() == "TEST GROUP":
            yield from simulated_stream("test group...")
            yield W("@@@")
            metadata = {
                "actionList": [
                    {
                        "type": "group",
                        "label": "A Group",
                        "children": [
                            {
                                "type": "button",
                                "params": {},
                                "label": "Explore",
                                "desc": "Explore what others are doing on-chain",
                                "message": "I want to see what others are doing with C-2AO."
                            },
                        ] * 3,
                    }
                ]
            }
            yield W(metadata)
            yield W(end=True)
            return


        # Check if user has a clear intent in the last message
        if "label" in last_message:
            if last_message["label"] == "Contract-to-Action":
                yield from c2a(data)
                return
            elif last_message["label"] == "Login":
                address = try_get_user_address(data)
                yield from simulated_stream(f"Let me check the wallet [{address}](https://sepolia.basescan.org/address/{address}) first...")
                yield W("@@@")
                prev_action = get_prev_action(history)
                yield W(prev_action)
                yield W(end=True)
                return
            elif last_message["label"] == "Unlock" or last_message["label"] == "Skip, Unlock Agent Wallet":
                wallet = get_agent_wallet(try_get_user_address(data))
                agent_address = wallet.default_address.address_id
                yield from simulated_stream(f"You have unlocked agent wallet for this session: {agent_address}.\n\n")
                yield from simulated_stream(f"(To run transactions with agent wallet, you usually need to transfer some funds to this address.)\n\n")

                yield from simulated_stream(f"The C-2AO agent can act on your behalf to execute the same transaction you just did. Or, you can also set a cronjob to run the same transaction periodically. Would you like to proceed?")

                yield W("@@@")
                yield W({"actionList": [
                    {
                        "type": "button",
                        "params": {},
                        "label": "Run Once",
                        "desc": "Run the transaction once",
                        "message": "Run the transaction once"
                    },
                    {
                        "type": "button",
                        "params": {},
                        "label": "Set Cron",
                        "desc": "Set a cronjob to run the transaction periodically",
                        "message": "Set a cronjob to run the transaction periodically"
                    },
                ], "agent_addr": agent_address})
                yield W(end=True)
                return
            elif last_message["label"] == "Run Once" or last_message["label"] == "Set Cron":
                found_action = None
                for msg in history[::-1]:
                    if 'actionList' in msg:
                        for act in msg['actionList']:
                            if act['type'] == 'invoke_tx':
                                found_action = act
                                break
                        if found_action is not None:
                            break
                if found_action is None:
                    yield from simulated_stream(f"Failed to find the transaction.")
                elif last_message["label"] == "Run Once":
                    yield from simulated_stream(f"Agent is running the transaction for you.")
                    wallet = get_agent_wallet(try_get_user_address(data))
                    params = found_action['params']
                    abi = params['abi']
                    args_list = params['args'] 
                    # we need to convert list to dict
                    args_dict = {}
                    for func in abi:
                        if func['type'] == 'function' and func['name'] == params['functionName']:
                            for (a, b) in zip(args_list, func['inputs']):
                                args_dict[b['name']] = a
                    tx = wallet.invoke_contract(params['address'], params['functionName'], abi, args_dict)
                    tx.wait()
                    yield from simulated_stream(f"Transaction hash: [{tx.transaction_hash}]({tx.transaction_link})")
                else:
                    yield from simulated_stream(f"Agent has set up the cronjob for you.")
                    # FIXME: set a cronjob to run the transaction periodically
                yield W("@@@")
                yield W({"actionList": []})
                yield W(end=True)
                return
            elif last_message["label"] == "Explore":
                yield from simulated_stream(G("Rephrase this and remove file suffix, make sure the format is an address:\n\n Hi, here is a list of contracts that others have explored: " + ",".join(os.listdir("./cache/raw_source"))))
                yield W("@@@")
                yield W({"actionList": [
                    {
                        "type": "button_ask_contract",
                        "params": {},
                        "label": "Contract-to-Action",
                        "desc": "Convert a smart contract into an agentic action",
                        "message": "Help me check <contract_address> on <network_id>."
                    },
                    {
                        "type": "button_login",
                        "params": {},
                        "label": "Login & Guess why I'm here",
                        "desc": "Login to help agent understand how it can help you",
                    },
                ]})
                yield W(end=True)
            elif last_message["label"] == "Invoke Tx":
                yield from agent_task(data)
                return
            elif selected_contract_action(data):
                a = selected_contract_action(data)
                yield from simulated_stream(f"You selected an action\n```json\n{json.dumps({'label': a['label'],'desc': a['desc'],'params': a.get('params', {})},indent=4)}\n```\n\n")
                user_address = try_get_user_address(data)
                contract_addr, network = try_get_contract_and_network(data)
                yield from simulated_stream("Checking login status and preparing CDP Action...\n")
                download_cdp_code_action = {
                    "type": "download",
                    "params": {
                        "content": generate_cdp_action(network+":"+contract_addr , a['params']['method'], "", 0),
                        "filename": "action.py"
                    },
                    "label": "Write CDP Action",
                    "desc": "Write CDP action code for this contract call",
                    "message": "Write CDP action code for me."
                }
                if user_address:
                    yield from simulated_stream("It seems you have logged in. Would you like me to prepare the transaction for you? Or, do you want to download CDP action code for this contract call?")
                    yield W("@@@")
                    yield W({"actionList": [
                        {
                            "type": "button",
                            "params": {},
                            "label": "Prepare Tx",
                            "desc": "Prepare the transaction for you",
                            "message": "Prepare the transaction for me."
                        },
                        download_cdp_code_action,
                    ]})
                else:
                    yield from simulated_stream("It seems you have not logged in. Would you like to login first so that I can prepare the transaction for you? Or do you want to download CDP action code for this contract call?")
                    yield W("@@@")
                    yield W({"actionList": [
                        {
                            "type": "button_login",
                            "params": {},
                            "label": "Login",
                            "desc": "Login to get context for transaction preparation",
                        },
                        download_cdp_code_action,
                    ]})
                yield W(end=True)
                return
            elif should_prepare_tx(data):
                yield from prepare_tx(data)
                return
            else:
                yield from simulated_stream("TODO: support other labels or use better error message")
                yield W("@@@")
                yield W({"actionList": []})
                yield W(end=True)
                return
        else:
            if len(history) >2 and "Invoke Tx" in [a.get("label", "") for a in history[-2]["actionList"]]:
                yield from prepare_tx(data)
            else:
                yield from simulated_stream(robust_reply(json.dumps(data, indent=2)))
                yield W("@@@")
                yield W({"actionList": []})
                yield W(end=True)
                return


@app.route('/api/message', methods=['POST'])
def message():
    if not request.is_json:
        return {"error": "Content-Type must be application/json"}, 400
    
    data = request.get_json()
    if 'message_id' not in data:
        return {"error": "message_id field is required"}, 400
    if 'history' not in data:
        return {"error": "history field is required"}, 400
    
    # Return a streaming response
    return Response(
        generate_response(data),
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
