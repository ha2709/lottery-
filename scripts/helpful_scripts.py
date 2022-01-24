from brownie import (\
    network, \
    config, accounts, MockV3Aggregator,\
     VRFCoordinatorMock,LinkToken,Contract, interface 
)  
# from brownie  import DECIMAL
# from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development","ganache-local"]
FORKED_LOCAL_ENVIROMENTS =["mainnet-fork","mainnet-fork-dev-1"]
DECIMAL = 8
INITIAL_VALUE =20000000000
contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,

}

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    elif network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS or \
          network.show_active() in FORKED_LOCAL_ENVIROMENTS:
        return accounts[0]
    else:
        return accounts.add(config['wallets']['from_key'])


def get_contract(contract_name):
    """
    This function will grab the contract addresses from brownie config
    if defined , otherwise, it will deploy a mock version of that contract,
    and return that mock contract. 
    Args:
        contract_name: string
    Returns:
        The most recently deployed version of this contract. 
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        if len(contract_type) <=0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config['networks'][network.show_active()][contract_name]
        # address
        # ABI
        contract =  Contract.from_abi (contract_type._name, contract_address, contract_type.abi)
    return contract
    
def deploy_mocks(decimals=DECIMAL, initial_value=INITIAL_VALUE):
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(decimals, initial_value,{"from": account})
    link_token = LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address, {"from":account})
    print("Deployed")

def fund_with_link(contract_address, account=None, link_token=None, amount=10000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount,{"from":account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from":account})
    tx.wait(1)
    print("Fund Contract")
    return tx
