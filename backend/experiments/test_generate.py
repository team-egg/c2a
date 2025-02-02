from actions.generate_cdp_action import generate_cdp_action

a = {'address': 'sepolia.base:0x19B57F2Ee33bcFDE75c1496B3752D099fc408Ef1', 'method': 'approve(address,uint256)', 'parameters': '{"spender":"0xb6cE7b211D80442b0E5A689fCe34892FF46829c1","amount":"1"}', 'value': '0'}
code = generate_cdp_action(**a)
open('generated_code.py', 'w').write(code)