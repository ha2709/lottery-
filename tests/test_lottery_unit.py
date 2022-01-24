#0.019
from brownie import Lottery, accounts,config, network, exceptions
from web3 import Web3
import pytest
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import *

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.25,"ether")
    assert expected_entrance_fee == entrance_fee
    # 1900000000000

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery = deploy_lottery()   
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from":get_account(), "value":lottery.getEntranceFee()})

def test_can_start_and_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery = deploy_lottery() 
    account = get_account()       
    lottery.startLottery({"from":account})
    lottery.enter({"from":account, "value":lottery.getEntranceFee()})
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
            pytest.skip()
    lottery = deploy_lottery()   
    account = get_account()         
    lottery.startLottery({"from":account})
    lottery.enter({"from":account, "value":lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from":account})
    assert lottery.lottery_state() == 2

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
    # request_id = transaction.events["RequestedRandomness"]["requestedId"]
    # STATIC_RNG = 777
    # get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from":account
    # })
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery