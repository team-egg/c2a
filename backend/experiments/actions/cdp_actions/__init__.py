from dotenv import load_dotenv
load_dotenv()

from . import analyze
from . import get_all_balances
from . import invoke_contract
from . import read_contract

from cdp_agentkit_core.actions import CDP_ACTIONS
CDP_ACTIONS.append(analyze.AnalyzeContractAction())
CDP_ACTIONS.append(analyze.GetContractFunctionDetailsAction())
CDP_ACTIONS.append(get_all_balances.GetAllBalanceAction())
CDP_ACTIONS.append(invoke_contract.InvokeContractAction())
CDP_ACTIONS.append(read_contract.ReadContractAction())
# hacky way to add the new action to the CDP_ACTIONS list