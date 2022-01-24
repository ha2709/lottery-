// SPDX-License-Identifier:MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {

    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    address payable public recentWinner;
    uint256 public randomness;
    bytes32 public keyHash;
    uint256 public fee;
    event RequestedRandomness(bytes32 requestId);
    LOTTERY_STATE public lottery_state;

    constructor(address _priceFeedAddress,
    address _vrfCoordinator,
     address _link,
     uint256 _fee,
     bytes32 _keyHash) public VRFConsumerBase(_vrfCoordinator,_link ) {
        usdEntryFee = 50*(10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }
    function enter() public payable {
        require(lottery_state == LOTTERY_STATE.OPEN);
        require(msg.value >=getEntranceFee(), "Not Enough ETH! ");
        players.push(msg.sender);
    }
    function getEntranceFee() public view returns (uint256) {
        (,int price, ,,) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price)* 10 **10;
        uint256 costToEnter = (usdEntryFee *10 **18)/adjustedPrice;
        return costToEnter;
    }
    function startLottery() public onlyOwner {
        require(lottery_state ==  LOTTERY_STATE.CLOSED,"Can't start a new lottery yet ");
        lottery_state = LOTTERY_STATE.OPEN;
    }
    function endLottery() public onlyOwner{
        // uint(
        //     keccack256(
        //         abi.encodePacked(
        //             nonce,
        //             msg.sender,
        //             block.difficulty,
        //             block.timestamp
        //         )
        //     )
        // ) % players.length;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
    
        require(lottery_state ==LOTTERY_STATE.CALCULATING_WINNER, "You aren't there yet!");
        require(_randomness >0, "random-not-found");
        uint256 indexOfWiner = _randomness % players.length;
        recentWinner = players[indexOfWiner];
        recentWinner.transfer(address(this).balance);
        // Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}