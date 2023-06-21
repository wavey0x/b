from brownie import Contract, accounts
from eth_account import Account
import click

def main():
    ms = "0x7d2aB9CA511EBD6F03971Fb417d3492aA82513f0"
    fallback = Contract("0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4")
    me = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))

    message = "0x1109174f05b76e193717f67e51ef98c6f707478ab32d1e501ac02451a0020756"

    hash_to_sign = bytes(fallback.getMessageHashForSafe(ms, message))
    print(f"hash_to_sign: {hash_to_sign.hex()}")

    signature = me._acct.signHash(hash_to_sign)
    print(f"will sign with {signature.signature.hex()}")

