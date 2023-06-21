import requests
import os, telebot, time
from brownie import accounts, web3, Contract, chain, ZERO_ADDRESS, interface
from web3._utils.events import construct_event_topic_set
from datetime import datetime, date
from dotenv import load_dotenv
import json
import warnings
import logging
import pandas as pd
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", ".*is in the process.*")

load_dotenv()
account = os.environ.get("ACCOUNT")
TRUEBLOCKS_NODE_URL = os.environ.get("TRUEBLOCKS_NODE_URL")
TRUEBLOCKS_NODE_PORT = os.environ.get("TRUEBLOCKS_NODE_PORT")
ETHERSCAN_KEY = os.environ.get("ETHERSCAN_KEY")
gauge_controller = ("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB")
address_provider = Contract('0x0000000022D53366457F9d5E68Ec105046FC4383')
curve_registry = Contract(address_provider.get_address(0))
registry = Contract("0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5")

telegram_bot_key = os.environ.get('WAVEY_ALERTS_BOT_KEY')
etherscan_base_url = f'https://etherscan.io/'
bot = telebot.TeleBot(telegram_bot_key)
env = os.environ.get("ENV")
sleep_time = int(os.environ.get("SLEEP_TIME"))

EXPLORER = {
    1: "etherscan",
    10: "optiscan",
    42161: "arbiscan",
}

CHAT_IDS = {
    "WAVEY_ALERTS": "-789090497",
    "CURVE_WARS": "-1001653990357",
    "GNOSIS_CHAIN_POC": "-1001516144118",
    "YBRIBE": "-1001862925311",
    "VEYFI": "-1001615931572",
    "SEASOLVER_SA": "-1001829083462",
    'PROXY_WATCHER': "-1001286921212",
}

IMPLEMENTATION_SLOT = '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
SCORE_THRESHOLD = 10_000

def main():
    c = Contract('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    contract = web3.eth.contract(c.address, abi=c.abi)
    ytrades = '0x7d2aB9CA511EBD6F03971Fb417d3492aA82513f0'
    topics = construct_event_topic_set(
        contract.events.Approval().abi, 
        web3.codec,
        {'src':ytrades}
    )
    logs = web3.eth.get_logs(
        { 'topics': topics, 'fromBlock': 13577493, 'toBlock': chain.height }
    )
    events = contract.events.Approval().processReceipt({'logs': logs})

    approvals = []
    for e in events:
        a = {}
        src, dst, amount = e.args.values()
        token = Contract(e.address)
        amount /= 10**token.decimals()
        print(f'{src} {dst} {amount}')
        a['token_address'] = token.address
        a['symbol'] = token.symbol()
        a['src'] = src
        a['dst'] = dst
        a['amt'] = amount
        a['is_contract'] = web3.eth.getCode(dst).hex() != '0x'
        a['date'] = datetime.utcfromtimestamp(chain[e.blockNumber].timestamp).strftime('%Y-%m-%d')
        approvals.append(a)

    df = pd.DataFrame(approvals)
    
    df.to_csv(f'data/ytrades-approvals.csv', index=False)

def get_score(address):
    try:
        # url = f'http://localhost:8080/list?addrs={address}&count=true'
        url = f'{TRUEBLOCKS_NODE_URL}:{TRUEBLOCKS_NODE_PORT}/list?addrs={address}&count=true'
        resp = requests.get(url).json()
        return int(resp['data'][0]['nRecords'])
    except:
        return 0

def get_emoji(score):
    # anything less than SCORE_THRESHOLD=10_000 is ignored
    if score < 50_000:
        return "🔵"
    elif score < 150_000:
        return "🟡"
    elif score < 500_000:
        return "🔴"
    else:
        return "🔥"
    
def check_if_verified(proxy, implementation):
    url = f'https://api.{EXPLORER[chain.id]}.com/api?module=contract&action=getabi&address={implementation}&apikey={ETHERSCAN_KEY}'
    data = requests.get(url).json()
    if data['status'] == 0:
        print(f'Implementation source not verified on explorer {implementation}')
        return False
    return True