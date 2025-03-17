// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract LanguageDAO {
    struct Proposal {
        bytes32 proposalHash;
        uint256 voteStart;
        uint256 voteEnd;
        uint256 yesVotes;
        uint256 noVotes;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(bytes32 => bool) public usedHashes;
    uint256 public proposalCount;
    bytes32 public merkleRoot;
    
    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }
    
    function submitProposal(
        bytes32 proposalHash, 
        bytes32[] calldata proof
    ) external {
        require(block.timestamp > 1640995200, "Genesis period ongoing");
        bytes32 txHash = keccak256(abi.encodePacked(tx.origin));
        require(!usedHashes[txHash], "Duplicate submission");
        usedHashes[txHash] = true;
        
        require(verifyProof(proof, msg.sender), "Not authorized");
        
        proposals[proposalCount++] = Proposal({
            proposalHash: proposalHash,
            voteStart: block.timestamp,
            voteEnd: block.timestamp + 7 days,
            yesVotes: 0,
            noVotes: 0
        });
    }
    
    function vote(uint256 proposalId, bool support) external {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp < p.voteEnd, "Voting ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        
        if(support) p.yesVotes += 1;
        else p.noVotes += 1;
        hasVoted[proposalId][msg.sender] = true;
    }
    
    function verifyProof(
        bytes32[] memory proof,
        address voter
    ) internal view returns (bool) {
        bytes32 leaf = keccak256(abi.encodePacked(voter));
        return MerkleProof.verify(proof, merkleRoot, leaf);
    }
}
