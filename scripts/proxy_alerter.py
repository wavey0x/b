import requests
import os, telebot, time
from brownie import accounts, web3, Contract, chain, ZERO_ADDRESS, interface
from web3._utils.events import construct_event_topic_set
from datetime import datetime, date
from dotenv import load_dotenv
import json
import warnings
import logging
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
    start_block = 17_211_973
    with open("local_data.json", "r") as jsonFile:
        data = json.load(jsonFile)
        start_block = data['last_block']
    
    finish_block = 0
    while True:
        finish_block = search(max(start_block, finish_block))
        print(f'Reached chain head {finish_block}. Sleeping for {sleep_time} seconds...')
        data = {}
        data['last_block'] = finish_block
        with open("local_data.json", 'w') as fp:
            json.dump(data, fp, indent=2)
        time.sleep(sleep_time)

def search(start_block):
    c = interface.IProxy('0xE95A203B1a91a908F9B9CE46459d101078c2c3cb')
    contract = web3.eth.contract(c.address, abi=c.abi)
    
    topics = construct_event_topic_set(
        contract.events.Upgraded().abi, 
        web3.codec,
        {}
    )
    logs = web3.eth.get_logs(
        { 'topics': topics, 'fromBlock': start_block, 'toBlock': chain.height }
    )
    events = contract.events.Upgraded().processReceipt({'logs': logs})

    for e in events:
        implementation = e.args.values()
        proxy = e.address
        score = get_score(proxy)
        block = e.blockNumber
        if score < SCORE_THRESHOLD:
            print(f'{proxy} scored {score} which is less than {SCORE_THRESHOLD} threshold, skipping | proceesed block {block}')
            continue
        emoji = get_emoji(score)
        implementation = web3.toChecksumAddress('0x'+web3.eth.getStorageAt(proxy, IMPLEMENTATION_SLOT).hex()[26:])
        if implementation == ZERO_ADDRESS:
            print(f'Skipping {proxy} ... implementation slot not set')
            continue
        # verified = check_if_verified(proxy, implementation)
        url = f'https://upgradehub.xyz/diffs/{EXPLORER[chain.id]}/{proxy}'
        txn_hash = e.transactionHash.hex()
        try:
            tx = chain.get_transaction(txn_hash)
        except:
            continue
        ts = int(tx.timestamp)
        event_date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        name = ''
        try:
            name = Contract(proxy).name()
        except:
            pass
        
        msg = f' _Name not found_ | Score *{score:,}* {emoji}'
        if name != '':
            msg = f'*{name}* | Score: *{score:,}* {emoji}'
        msg += f'\n\nProxy: [{proxy}](https://etherscan.io/address/{proxy})'
        msg += f'\nImpl: [{implementation}](https://etherscan.io/address/{implementation})'
        msg += f'\nUpgraded at: {event_date}  '
        msg += f'[View txn](https://etherscan.io/tx/{txn_hash})'
        msg += f'\n\n🔗[View on DIFF on UpgradeHub]({url})'
        print(msg)
        chat_id = CHAT_IDS["PROXY_WATCHER"] if env == "PROD" else CHAT_IDS["WAVEY_ALERTS"]
        bot.send_message(chat_id, msg, parse_mode="markdown", disable_web_page_preview = True, timeout=60)
        time.sleep(5)

    return chain.height

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