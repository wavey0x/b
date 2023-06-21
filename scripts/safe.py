from ape_safe import ApeSafe
from brownie import ZERO_ADDRESS, Contract

def main():
    safe = ApeSafe('ytrades.ychad.eth')
    s = Contract(safe.address)
    stx = safe.build_multisig_tx(safe.address, 0, s.setGuard.encode_input(ZERO_ADDRESS))
    print(stx.safe_tx_hash)
    # should be 0xf8a7a3fa4f67910f5edcca139f0ddbe5043fb13f040b2a636e52b40d64c596d4
    print(safe.sign_transaction(stx, 'wavey2'))