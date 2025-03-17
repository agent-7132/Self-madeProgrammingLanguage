pragma solidity ^0.8.0;
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@semver/contracts/Semver.sol";

contract PackageRegistry {
    using ECDSA for bytes32;
    using Semver for string;
    
    struct Package {
        address publisher;
        string version;
        bytes32 checksum;
        uint256 timestamp;
    }
    
    mapping(string => Package[]) public packages;
    mapping(bytes32 => bool) public publishedHashes;
    mapping(bytes32 => bool) public publishedVersions;
    
    event PackagePublished(string indexed name, string version, address publisher);

    function validateVersion(string memory version) internal pure {
        require(version.isValid(), "Invalid semver");
        (uint256 major, uint256 minor, uint256 patch) = version.parse();
        require(major > 0 || minor > 0 || patch > 0, "版本号保留");
    }

    function publish(
        string calldata name,
        string calldata version,
        bytes32 checksum,
        bytes memory signature
    ) external {
        validateVersion(version);
        require(bytes(name).length <= 64, "名称过长");
        
        bytes32 messageHash = keccak256(abi.encodePacked(name, version, checksum));
        address signer = messageHash.toEthSignedMessageHash().recover(signature);
        require(signer == msg.sender, "签名无效");
        
        bytes32 versionHash = keccak256(bytes(version));
        require(!publishedVersions[versionHash], "重复版本");
        require(!publishedHashes[checksum], "重复包");

        packages[name].push(Package({
            publisher: msg.sender,
            version: version,
            checksum: checksum,
            timestamp: block.timestamp
        }));
        
        publishedHashes[checksum] = true;
        publishedVersions[versionHash] = true;
        emit PackagePublished(name, version, msg.sender);
    }

    function verify(
        string calldata name,
        string calldata version,
        bytes32 checksum
    ) external view returns (bool) {
        Package[] storage vers = packages[name];
        bytes32 targetVersion = keccak256(bytes(version));
        for (uint i = 0; i < vers.length; i++) {
            if (keccak256(bytes(vers[i].version)) == targetVersion && 
                vers[i].checksum == checksum) {
                return true;
            }
        }
        return false;
    }
}
