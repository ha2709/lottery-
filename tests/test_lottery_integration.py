  #0.019
from brownie import Lottery, accounts,config, network
from scripts.deploy_lottery import deploy_lottery;
from web3 import Web3
import time
import pytest
from scripts.helpful_scripts import *


def test_can_pick_winner():
  if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
    pytest.skip()
  lottery = deploy_lottery()
   
  account = get_account()         
  lottery.startLottery({"from":account})
  lottery.enter({"from":account, "value":lottery.getEntranceFee()})
  lottery.enter({"from":get_account(index=1), "value":lottery.getEntranceFee()})
  lottery.enter({"from":get_account(index=2), "value":lottery.getEntranceFee()})
  fund_with_link(lottery)
  transaction = lottery.endLottery({"from": account})
  time.sleep(60)
  assert lottery.recentWinner() == account
  assert lottery.balance() == 0
  # assert account.balance() == starting_balance_of_account + balance_of_lottery 