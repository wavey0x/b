import requests
import time
import pandas as pd
from brownie import web3, ZERO_ADDRESS, Contract, chain

WEEK = 60 * 60 * 24 * 7

def main():
    voter = web3.ens.resolve('curve-voter.ychad.eth')
    # url = 'https://snapshot-mirror.prod.stake.capital/bribes?name=stake-dao'
    url = 'https://vm.crvusd.fi/bribes?name=stake-dao'
    data = requests.get(url).json()
    for d in data:
        if d['label'] == 'Curve':
            data = d
            break

    bribes = data['bribes']
    bribe_contract = Contract(data['bribeContract'])
    gauge_controller = Contract(data['gaugeController'])
    current_time = int(time.time())
    current_period = bribe_contract.getCurrentPeriod()
    next_period = current_period + WEEK

    display_columns = [
        'gauge',
        'gaugeName',
        'token_symbol',
        'token_price',
        'gaugeWeight',
        # 'rewardToken', 
        'totalVotes', 
        'manual_calc',
        'yearnVotes',
        # 'totalRewardAmountUSD',
        'rewardsAvailable',
        'rewardsAvailableUSD',
        'yearn_current_power',
    ]
    new_bribes = []
    for bribe in bribes:
        if not bribe['active'] or voter in bribe['blacklistedAddresses']: #bribe['closed'] or (next_period <= bribe['endTimestamp'])
            continue
        token_info = bribe['rewardToken']
        bribe['id'] = int(bribe['newBribeID']['hex'],16)
        bribe['totalRewardAmount'] = int(bribe['totalRewardAmount']['hex'],16) / 10 ** bribe['rewardTokenDecimals']
        bribe['totalRewardPerPeriod'] = int(bribe['totalRewardPerPeriod']['hex'],16) / 10 ** bribe['rewardTokenDecimals']
        bribe['token_price'] = token_info['price']
        bribe['token_symbol'] = token_info['symbol']

        bribe['gaugeWeight'] = int(bribe['gaugeWeight']['hex'],16) / 10 ** 18

        total_weight = gauge_controller.points_weight(bribe['gauge'], next_period)['bias'] # Total weight
        banned_amount = 0
        for banned in bribe['blacklistedAddresses']:
            user_slope = gauge_controller.vote_user_slopes(banned, bribe['gauge']) # User weight
            banned_amount += get_bias(user_slope['slope'], user_slope['end'], next_period)
        bribe['manual_calc'] = (total_weight - banned_amount) / 10 ** 18

        user_slope = gauge_controller.vote_user_slopes(voter, bribe['gauge']) # User weight
        bribe['yearnVotes'] = get_bias(user_slope['slope'], user_slope['end'], current_period) / 10 ** 18
        bribe['yearn_current_power'] = user_slope['power']

        new_bribes.append(bribe)
        # print(f'{bribe["gaugeName"]}')

    df = pd.DataFrame(new_bribes, columns=display_columns)
    
    print(df)
    df.to_csv("gauges.csv", index=False)
    assert False

def get_bias(slope,  end, current_period):
    return slope * (end - current_period)

def simulate_lock():
    g = web3.ens.resolve('ychad.eth')
    p = Contract(web3.ens.resolve('curve-proxy.ychad.eth'), owner=g)
    p.lock()
    p.maxLock()
    v = Contract(web3.ens.resolve('curve-voter.ychad.eth'))
    ve = Contract(v.escrow(), owner=v)

    bal = ve.balanceOf(v)/1e18
    print(f'Balance: {bal}')

def gauge_bias(gauge):
    current_period = int(chain.time()/WEEK) * WEEK
    next_period = current_period + WEEK
    v = web3.ens.resolve('curve-voter.ychad.eth')
    gauge_controller = Contract('0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB')
    user_slope = gauge_controller.vote_user_slopes(v, gauge) # User weight
    bias = get_bias(user_slope['slope'], user_slope['end'], next_period)
    print(f'{bias/1e18}')
    print(f'{bias/1e18}')