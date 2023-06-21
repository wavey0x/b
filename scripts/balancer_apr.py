import web3
from datetime import datetime
from brownie import Contract, ZERO_ADDRESS, chain, accounts, interface
from enum import Enum
from brownie.convert import to_bytes
from eth_abi import encode
from y import get_price


def main():
    WEEK = 60 * 60 * 24 * 7
    period_totals = {}
    periods = []
    distributor = Contract('0xD3cf852898b21fc233251427c2DC93d3d604F3BB')
    ve_bal = Contract('0xC128a9954e6c874eA3d62ce62B468bA073093F25')
    start_block = 16_000_000
    end_block = chain.height
    logs = distributor.events.TokenCheckpointed.getLogs(fromBlock=start_block)
    for log in logs:
        token, amount, last_token_time = log.args.values()
        token = Contract(token)
        decimals = token.decimals()
        amount = amount / 10 ** decimals
        block = log['blockNumber']
        ts = chain[block]['timestamp']
        period = int(ts / WEEK) * WEEK
        if token.address == '0xA13a9247ea42D743238089903570127DdA72fE44':
            usd_value = amount
        else:
            usd_value = get_price(token.address, block) * amount
        if period in period_totals:
            period_totals[period]['usd_value'] += usd_value
        else:
            p = {
                'usd_value': usd_value,
                'block': block,

            }
            period_totals[period] = p
            periods.append(period)
        date_str = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        

    print(f'\n---WEEKLY TOTALS---\n')

    for period in periods:
        date_str = datetime.utcfromtimestamp(period).strftime('%Y-%m-%d %H:%M:%S')
        total_supply_at_block = ve_bal.totalSupply(block_identifier=period_totals[period]['block']) / 1e18
        print(f'{date_str} | {period} | ${period_totals[period]["usd_value"]:,.2f} | {total_supply_at_block:,.2f}')
    assert False
    distributor.TokenCheckpointed
