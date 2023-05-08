import requests
import time
import pandas as pd
from brownie import web3, ZERO_ADDRESS, Contract, chain
from multisig_ci.ci_override import DelegateSafe as ApeSafe
from multisig_ci.safes import safe
from multisig_ci.sign import sign
from multisig_ci.safes import safe
from multisig_ci.sign import sign

WEEK = 60 * 60 * 24 * 7

def main():
    gauge_vote_05_03_2023()

def gauge_vote_05_03_2023():
    safe = ApeSafe("amigos.ychad.eth")
    
    gauges = {
        # FIXED STUFF #
        "0x5980d25B4947594c26255C0BF301193ab64ba803": 1_000,    # YCRV
        "0x8133e6b0b2420bba10574a6668ea275f5e7ed253": 124,      # STG/FRAXBP (NEW)
        "0x05255C5BD33672b9FEA4129C13274D1E6193312d": 300,      # YFI/ETH
        "0x875CE7e0565b4C8852CA2a9608F27B7213A90786": 3_700,    # TANGIBLE

        # VARIABLE STUFF #
        "0x1cEBdB0856dd985fAe9b8fEa2262469360B8a3a6": 75,      # CRV-WETH
        "0xDeFd8FdD20e0f34115C7018CCfb655796F6B2168": 1_375,    # TriCrypto
        "0xe5d5aa1bbe72f68df42432813485ca1fc998de32": 1_901,    # LDO/ETH
        "0x40371aad2a24ed841316ef30938881440fd4426c": 625,      # poly-crv+crvusdbtceth
        "0x555766f3da968ecBefa690Ffd49A2Ac02f47aa5f": 900,      # arbi-USDT+WBTC+WETH 
        
        # DEPRECATED STUFF #
        "0xc25836ad05f14b7161638edc67fd9c65b19f0c5a": 0,        # eth+matic
        "0x95d16646311fDe101Eb9F897fE06AC881B7Db802": 0,        # STG/USDC
        "0xacc9f5cedc631180a2ad4c945377930fcfcc782f": 0,        # TRYB/3CRV
        "0x3c0ffff15ea30c35d7a85b85c0782d6c94e1d238": 0,        # eth+seth (NEW)
        "0xa90996896660decc6e997655e065b23788857849": 0,        # 3crv+susd (NEW)
        "0x0e2f214b8f5d0cca011a8298bb907fb62f535160": 0,        # poly-matic+crvusdbtceth
        "0xBE266d68Ce3dDFAb366Bb866F4353B6FC42BA43c": 0,        # DOLA/FRAXBP
        "0x8f162742a7BCDb87EB52d83c687E43356055a68B": 0,        # Temple
        "0x9582C4ADACB3BCE56Fea3e590F05c3ca2fb9C477": 0,        # alusd+3crv (NEW)
        "0xd8b712d29381748dB89c36BCa0138d7c75866ddF": 0,        # MIM
        "0x12dcd9e8d1577b5e4f066d8e7d404404ef045342": 0,      # eth+aleth (NEW)
        "0x740ba8aa0052e07b925908b380248cb03f3de5cb": 0,      # alusd+fraxbp (NEW)
    }

    assert len(gauges.keys()) > 0
    voter = safe.contract("curve-voter.ychad.eth")
    proxy = safe.contract("curve-proxy.ychad.eth")
    gauge_controller = safe.contract("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB")

    # Re-lock logic
    proxy.lock()
    DAY = 60 * 60 * 24
    WEEK = 7 * DAY
    MAXTIME = 4 * 365 * DAY
    vecrv = safe.contract("0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2")
    lock = vecrv.locked(proxy).dict()
    remaining = lock["end"]
    if remaining > MAXTIME - WEEK:
        print("Cannot extend")
    else:
        proxy.maxLock()

    gain_group = {}
    for g in gauges:
        old_weight = gauge_controller.vote_user_slopes(voter, g).dict()["power"]
        new_weight = gauges[g]
        if old_weight > new_weight:
            proxy.vote(g, new_weight)
        elif not (old_weight == 0 and new_weight == 0):
            gain_group[g] = new_weight

    # Vote for this group last since they gain weight
    for g in gain_group:
        proxy.vote(g, gain_group[g])

    assert gauge_controller.vote_user_power(voter) == 10_000 # Ensure we've maximized votes

    # These lines will handle posting the transaction
    safe_tx = safe.multisend_from_receipts()
    safe.preview(safe_tx, call_trace=False)
    safe.post_transaction(safe_tx)