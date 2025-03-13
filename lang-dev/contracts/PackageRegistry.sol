pragma solidity ^0.8.0;
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

contract PackageRegistry {
    using ECDSA for bytes32;
    
    struct Package {
        address publisher;
        string version;
        bytes32 checksum;
        uint256 timestamp;
    }
    
    mapping(string => Package[]) public packages;
    mapping(bytes32 => bool) public publishedHashes;
    
    event PackagePublished(
        string indexed name,
        string version,
        address publisher
    );
    
    function publish(
        string calldata name,
        string calldata version,
        bytes32 checksum,
        bytes memory signature
    ) external {
        bytes32 messageHash = keccak256(abi.encodePacked(name, version, checksum));
        address signer = messageHash.toEthSignedMessageHash().recover(signature);
        
        require(signer == msg.sender, "Invalid signature");
        require(!publishedHashes[checksum], "Duplicate package");
        
        packages[name].push(Package({
            publisher: msg.sender,
            version: version,
            checksum: checksum,
            timestamp: block.timestamp
        }));
        
        publishedHashes[checksum] = true;
        emit PackagePublished(name, version, msg.sender);
    }
    
    function verify(
        string calldata name,
        string calldata version,
        bytes32 checksum
    ) external view returns (bool) {
        Package[] storage vers = packages[name];
        for (uint i = 0; i < vers.length; i++) {
            if (keccak256(bytes(vers[i].version)) == keccak256(bytes(version)) &&
                vers[i].checksum == checksum) {
                return true;
            }
        }
        return false;
    }
}
