import os
import requests
import json
from io import StringIO
from slither import Slither
from crytic_compile.crytic_compile import compile_all, CryticCompile
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

ETHERSCAN_KEY = os.getenv('ETHERSCAN_KEY')
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

dirname = os.path.dirname(__file__)
system_prompt = open(os.path.join(dirname, 'analyze_prompt.txt')).read()

def analyze(contract_address):
    contract_address = contract_address.lower()

    os.makedirs('cache/analysis', exist_ok=True)
    os.makedirs('cache/abi', exist_ok=True)
    os.makedirs('cache/raw_source', exist_ok=True)

    filename = f'cache/analysis/{contract_address}.json'
    filename2 = f'cache/abi/{contract_address}.json'
    if not os.path.exists(filename):
        analysis, abi = _analyze(contract_address)
        open(filename, 'w').write(json.dumps(analysis))
        open(filename2, 'w').write(json.dumps(abi))
    analysis = json.loads(open(filename).read())
    abi = json.loads(open(filename2).read())

    filename = f'cache/raw_source/{contract_address}.json'
    if not os.path.exists(filename):
        result = _get_raw_source(contract_address)
        open(filename, 'w').write(json.dumps(result))
    raw_source = json.loads(open(filename).read())

    return {
        'analysis': analysis,
        'raw_source': raw_source,
        'abi': abi,
    }

def _analyze(contract_address):
    print('analyze', contract_address)
    compile = CryticCompile(contract_address, etherscan_api_key=ETHERSCAN_KEY, export_dir='cache/compile')

    compilation_units = list(compile.compilation_units.values())
    assert len(compilation_units) == 1
    compilation_unit = compilation_units[0]
    contract_name = compilation_unit.unique_id
    print('contract name', contract_name)

    abis = []
    for source_unit in compilation_unit.source_units.values():
        if contract_name in source_unit.contracts_names:
            abis.append(source_unit.abi(contract_name))
    assert len(abis) == 1
    abi = abis[0]


    ai_summary_input = StringIO()
    delim = '-' * 20

    print(f'The main contract is **{contract_name}**.', file=ai_summary_input)
    print('You need to handle these source files:', file=ai_summary_input)
    print(delim, file=ai_summary_input)

    for filename in compilation_unit.filenames:
        content = open(filename.absolute, 'rb').read().decode('utf-8', 'ignore')
        print('File:', filename.short, file=ai_summary_input)
        print(delim, file=ai_summary_input)
        print(content, file=ai_summary_input)
        print(delim, file=ai_summary_input)

    print(f'The main contract is **{contract_name}**.', file=ai_summary_input)
    print('You need to handle these functions:', file=ai_summary_input)
    print(delim, file=ai_summary_input)

    slither = Slither(compile)
    contracts = slither.get_contract_from_name(contract_name)
    assert len(contracts) == 1
    contract = contracts[0]
    #contract.compilation_unit.


    for fn in contract.functions:
        contract_name, name, visibility, modifiers, vars_read, vars_written, internal_calls, external_calls_as_expressions, _ = fn.get_summary()
        if visibility in ['public', 'external']:
            print('Function:', fn.name, file=ai_summary_input)
            print(f'Unique name: **{name}**', file=ai_summary_input)
            print('Visibility:', visibility, file=ai_summary_input)
            print('Modifiers:', modifiers, file=ai_summary_input)
            print('Variables read:', vars_read, file=ai_summary_input)
            print('Variables written:', vars_written, file=ai_summary_input)
            print('Internal calls:', internal_calls, file=ai_summary_input)
            print('External calls:', external_calls_as_expressions, file=ai_summary_input)
            print(delim, file=ai_summary_input)

    prompt = ai_summary_input.getvalue()
    # open('test.txt', 'w').write(prompt)

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
    
    print('compile ok, now use gpt to analyze')
    response = openai_client.chat.completions.create(
        model="o3-mini",
        messages=prompt_messages,
    )
    #open('response.txt', 'w').write(response.choices[0].message.content)
    analysis = json.loads(response.choices[0].message.content)
    return analysis, abi

def _get_raw_source(contract_address):
    chain, address = contract_address.split(':')
    if chain == 'base':
        chainid = 8453
    elif chain == 'sepolia.base':
        chainid = 84532
    else:
        raise Exception('Invalid chain')
    url = f'https://api.etherscan.io/v2/api?chainid={chainid}&module=contract&action=getabi&address={contract_address}&apikey={ETHERSCAN_KEY}'
    return requests.get(url).json()

if __name__ == '__main__':
    analyze('base:0x9e592de9Cd749005468Ae505395E1749524fBAFa')
    analyze('base:0x091e99cb1C49331a94dD62755D168E941AbD0693')
    analyze('sepolia.base:0x71EF937E2e84E1bE1181C3D2BF03AD86C36D3Fa1')
    #_analyze('base:0x9e592de9Cd749005468Ae505395E1749524fBAFa')
    pass