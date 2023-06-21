import requests
import time
import pandas as pd
from brownie import web3, ZERO_ADDRESS, Contract, chain
from multisig_ci.ci_override import DelegateSafe as ApeSafe
from multisig_ci.safes import safe
from multisig_ci.sign import sign
from multisig_ci.safes import safe
from multisig_ci.sign import sign
from brownie.convert import to_bytes
from eth_abi import encode

WEEK = 60 * 60 * 24 * 7

def main():
    bal_lock()

def bal_lock():
    safe = ApeSafe('ychad.eth')

    voter = safe.contract('bal-voter.ychad.eth')
    escrow = safe.contract(voter.escrow())
    token = safe.contract(escrow.token())
    duration = 60 * 60 * 24 * 365 # Max time
    voter.createLock(token.balanceOf(voter),chain.time() + duration)

    query_helper = Contract('0xE39B5e3B6D74016b2F6A9673D7d7493B6DF549d5')
    swap = (
        '0xd61e198e139369a40818fe05f5d5e6e045cd6eaf000000000000000000000540', # pool_id
        0,      # Kind
        '0x5c6Ee304399DBdB9C8Ef030aB642B10820DB8F56',  # BALWETH
        '0x98E86Ed5b0E48734430BfBe92101156C75418cad',  # YBAL
        1e18,   #amount
        b''
    )
    fund = (
        ZERO_ADDRESS,
        False,
        ZERO_ADDRESS,
        False
    )
    amount_ybal_per_balweth  = query_helper.querySwap.call(swap,fund)

    assert False

    # These lines will handle posting the transaction
    safe_tx = safe.multisend_from_receipts(safe_nonce=7)
    # safe.preview(safe_tx, call_trace=False)
    safe.post_transaction(safe_tx)