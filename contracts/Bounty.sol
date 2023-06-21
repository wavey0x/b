// pragma solidity 0.8.15;

// import '@openzeppelin/contracts/token/ERC20/IERC20.sol';

// interface IGuard {
//     function manager() returns(address);
//     function governor() returns(address);
//     function pendingManager() returns(address);
//     function pendingGovernor() returns(address);
// }
// contract Bounty {
//     using SafeERC20 for IERC20;

//     address constant gov = 0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52;
//     IERC20 constant dai = IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);
//     uint256 public constant offer = 10_000e18;
//     uint256 public constant deadline = 1687665600; // Sun Jun 25 2023 04:00:00 GMT+0000
//     address constant recipient = 0x3f67114235C694e881558F65Ba5CF000be323817; // Gnosis safe of attacker
//     IGuard constant guard = IGuard(0xa6A8B8F06835d44E53Ae871b2EadbE659c335e5d);


//     function claimBounty() external {
//         require(guard.manager() == gov);
//         require(guard.governor() == gov);
//         require(now < deadline);
//         dai.transfer(recipient, offer);
//     }

//     function retractBounty() external {
//         require(guard.pendingGovernor() != gov && guard.pendingManager() != gov);
//         require(msg.sender == gov);
//         require(now > deadline);
//         dai.transfer(gov, offer);
//     }

// }


