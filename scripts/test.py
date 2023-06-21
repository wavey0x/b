import requests
import time, datetime
from datetime import datetime
import pandas as pd
from brownie import web3, ZERO_ADDRESS, Contract, chain, interface

def main():
    # Initial API fetch of DAI 
    dai = Contract('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    print(f'version {dai.version()}')

    # Assign wrong interface
    dai = interface.IERC20('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    print(f'version {dai.version()}')

    # Fix the problem
    dai = Contract.from_explorer('0x6B175474E89094C44Da98b954EedeAC495271d0F')
    dai = interface.DAI('0x6B175474E89094C44Da98b954EedeAC495271d0F')