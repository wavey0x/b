pragma solidity 0.8.15;

contract Job {
    function performRawCall(address target, bytes calldata data) external payable {
        (bool success, bytes memory result) = target.call{value: msg.value}(data);
        require(success, "Raw call failed");
    }
}
