from .analyze import analyze
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
load_dotenv()
from functools import lru_cache


openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# use relative path instead
current = os.path.dirname(__file__)
system_prompt = open(os.path.join(current, 'generate_cdp_action_prompt.txt')).read()


@lru_cache
# This file has exactly same signature as the file cdp_actions/get_all_balances.py
def generate_cdp_action(address: str, method: str, parameters: str, value: str) -> str:
    try:
        t = analyze(address)
        s = t['analysis']
        a = t['abi']
    except Exception as e:
        return f"Error analyzing contract: {e}"
    address = address.split(':')[1]
    method_name = method.split('(')[0]
    if parameters == "":
        parameters_dict = {}
    else:
        parameters_dict = json.loads(parameters)
    
    function_signature = None
    for fs in s['functions']:
        print("Matching", fs.lower(), method.lower()+"(")
        if fs.lower().startswith(method.lower()+"("):
            function_signature = fs
            break

    function_name = function_signature.split('(')[0]
    for abi in a:
        if abi['type'] == 'function':
            if abi['name'] == function_name:
                break
    f = s['functions'][function_signature]
    if f is None:
        raise Exception(f"Function {function_signature} not found in contract {address}")
    prompt = f"Function {function_signature} details:\n"
    prompt += f"Raw ABI: {str(abi)}\n"
    prompt += f"Detailed Description: {f['detail']}\n"
    for i, x in enumerate(f['parameters']):
        prompt += f"Parameter {i}: {x}\n"
    prompt += f"Prerequisites: {f['prerequisites']}"

    prompt += '=' * 20 + '\n'

    prompt += "Example invocation:\n"
    prompt += f"Address: {address}\n"
    prompt += f"Method: {method_name}\n"
    # prompt += f"Parameters: {parameters}\n"
    # prompt += f"Value: {value}\n"

    prompt_messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": prompt
        },
    ]

    print('prepake ok, now use gpt to generate')
    response = openai_client.chat.completions.create(
        model="o3-mini",
        messages=prompt_messages,
    )

    code = response.choices[0].message.content
    return code
