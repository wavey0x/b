import web3
from brownie import Contract, ZERO_ADDRESS, chain, accounts, interface
from enum import Enum
from brownie.convert import to_bytes
from eth_abi import encode

txn_params = {
    'max_fee': 80e9,
    'priority_fee':1e6
}
class JoinKind(int, Enum):
    INIT = 0
    EXACT_TOKENS_IN_FOR_BPT_OUT = 1
    TOKEN_IN_FOR_EXACT_BPT_OUT = 2
    ALL_TOKENS_IN_FOR_EXACT_BPT_OUT = 3
    ADD_TOKEN = 4

def main():
    wavey = accounts.load('wavey2')
    voter = Contract('0xBA11E7024cbEB1dd2B401C70A83E0d964144686C')
    ybal = Contract('0x98E86Ed5b0E48734430BfBe92101156C75418cad', owner=wavey)
    token = Contract(voter.token(), owner=wavey)
    gov = voter.governance()
    INITIAL_BPT_SUPPLY = 2 ** (112) - 1

    half = int(token.balanceOf(wavey) / 2)
    to_mint = half
    half = half - 10 ** 16
    token.approve(ybal, 2**256-1)
    tx = ybal.mint(to_mint, txn_params)

    pool = interface.IPool('0xD61e198e139369a40818FE05F5d5e6e045Cd6eaF', owner=wavey)
    pool_id = to_bytes(pool.getPoolId(), "bytes32")
    vault = Contract(pool.getVault(),owner=wavey)
    tokens = list(vault.getPoolTokens(pool_id)[0])

    for t in tokens:
        t = Contract(t,owner=wavey)
        print(f'{t.balanceOf(wavey)}')
        print(f'{int(half)}')
        t.approve(vault, 2**256-1, txn_params)

    ###
    ### Adding Liquidity on Balancer
    ###
    pool = interface.IPool('0xD61e198e139369a40818FE05F5d5e6e045Cd6eaF', owner=wavey)
    vault = Contract(pool.getVault(),owner=wavey)
    tokens = list(vault.getPoolTokens(pool_id)[0])

    INITIAL_BPT_SUPPLY = 2 ** (112) - 1
    half = int(token.balanceOf(wavey) / 2)
    
    user_data = encode(
        ["uint256", "uint256[]"], # ABI
        (JoinKind.INIT.value, [
            half,
            half,
            INITIAL_BPT_SUPPLY
        ]),  # Amounts in
    )

    request = (
        tokens,                             # assets[]
        [half, half, INITIAL_BPT_SUPPLY],   # maxAmountsIn[]
        user_data,                          # userData
        False                               # fromInternalBalance
    )

    tx = vault.joinPool(
        pool_id,    # poolID
        wavey,      # sender
        wavey,      # recipient
        request,    # request
        txn_params
    )

    ###
    ### Adding Liquidity on Curve
    ###
    pool = Contract('0xDcEF968d416a41Cdac0ED8702fAC8128A64241A2', owner=wavey)
    half = int(token.balanceOf(wavey) / 2)
    pool.add_liquidity([half,half], 0, txn_params)


    assert False

