import requests
import os, telebot, time, json
from brownie import web3, Contract, chain
from web3._utils.events import construct_event_topic_set
from datetime import datetime, date
from dotenv import load_dotenv

CHAT_IDS = {
    'DEV': 123,
    'PROD': 321,
}
    
load_dotenv()
env = os.environ.get("ENV")
chat_id = CHAT_IDS["PROD"] if env == "PROD" else CHAT_IDS["DEV"]

TELEGRAM_BOT_KEY = os.environ.get('WAVEY_ALERTS_BOT_KEY')
bot = telebot.TeleBot(TELEGRAM_BOT_KEY)

dai = Contract('0x6B175474E89094C44Da98b954EedeAC495271d0F')
wbtc = Contract('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599')
weth = Contract('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')

aweth = Contract('0x030bA81f1c18d280636F32af80b9AAd02Cf0854e')
adai = Contract('0x028171bCA77440897B824Ca71D1c56caC55b68A3')
awbtc = Contract('0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656')

markets = [
    aweth,
    adai,
    awbtc
]

lens = Contract('0x507fA343d0A90786d86C7cd885f5C49263A91FF4')
morpho = Contract('0x777777c9898d384f785ee44acfe945efdff5f3e0')
oracle = Contract('0xA50ba011c48153De246E5192C8f9258A2ba79Ca9')

def main():
    # while True:
    #     # Total Borrows
    #     p2p_borrow_amount, pool_borrow_amount, total_borrow_amount = lens.getTotalBorrow() 
        
    #     # Market Specific Borrows
    #     for market in markets:
    #         p2p_amount, pool_amount = lens.getTotalMarketBorrow(market.address)
    #         p2p_amount /= 10 ** market.decimals()
    #         pool_amount /= 10 ** market.decimals()
    #         underlying_asset = Contract(market.UNDERLYING_ASSET_ADDRESS())
    #         quote_in_eth = oracle.getAssetPrice(underlying_asset.address)
    #         print(f'asset: {underlying_asset.symbol(block_identifier=17_000_000)} | p2p borrowed: {p2p_amount:,.2f}')

    #     # Do some alert condition
    #     if p2p_amount > 10_000_000:
    #         msg = 'Some alert text'
    #         bot.send_message(chat_id, msg, parse_mode="markdown", disable_web_page_preview = True, timeout=60)
    #     time.sleep(5)

    samples = []
    for block_number in range(16_000_000, 16_000_500, 100):
        sample = {}
        supply = dai.totalSupply(block_identifier=block_number)/1e18

        sample['supply'] = supply
        sample['block'] = block_number
        samples.append(sample)
        print(f'block: {block_number} | supply: {supply:,.2f}')
        time.sleep(1)

    

    # Insert some code to search for stuff on chain
    





    # Check local file to determine which block we start searching at
    with open("my_data.json", "a+") as jsonFile:
        data = json.load(jsonFile)
        if 'last_block' not in data:
            start_block = START_BLOCK
        else:
            start_block = data['last_block']

    # Write latest block
    data = {'last_block': chain.height}
    with open("my_data.json", 'w') as fp:
        json.dump(data, fp, indent=2)


