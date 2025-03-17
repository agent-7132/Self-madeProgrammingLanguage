// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeCast.sol";

contract LanguageDAO is ReentrancyGuard {
    using SafeCast for uint256;
    
    struct Proposal {
        bytes32 proposalHash;
        uint256 voteStart;
        uint256 voteEnd;
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        address executor;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(bytes32 => bool) public usedHashes;
    uint256 public proposalCount;
    bytes32 public merkleRoot;
    
    event ProposalExecuted(uint256 indexed proposalId, bool result);
    
    constructor(bytes32 _merkleRoot) {
        merkleRoot = _merkleRoot;
    }
    
    function submitProposal(
        bytes32 proposalHash, 
        bytes32[] calldata proof
    ) external {
        require(block.timestamp > 1640995200, "Genesis period ongoing");
        require(!usedHashes[proposalHash], "Duplicate proposal");
        require(proposalCount == 0 || proposals[proposalCount-1].voteEnd + 1 days < block.timestamp, 
            "Proposal cooldown");
        
        bytes32 leaf = keccak256(abi.encodePacked(tx.origin));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "Not authorized");
        
        proposals[proposalCount++] = Proposal({
            proposalHash: proposalHash,
            voteStart: block.timestamp,
            voteEnd: block.timestamp + 7 days,
            yesVotes: 0,
            noVotes: 0,
            executed: false,
            executor: address(0)
        });
        usedHashes[proposalHash] = true;
    }
    
    function vote(uint256 proposalId, bool support) external {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp < p.voteEnd, "Voting ended");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        
        if(support) p.yesVotes += 1;
        else p.noVotes += 1;
        hasVoted[proposalId][msg.sender] = true;
    }
    
    modifier executionLock(uint256 proposalId) {
        Proposal storage p = proposals[proposalId];
        require(p.executor == address(0), "Executing");
        p.executor = msg.sender;
        _;
        p.executor = address(0);
    }
    
    function executeProposal(uint256 proposalId) 
        external 
        nonReentrant 
        executionLock(proposalId) 
    {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp > p.voteEnd + 1 days, "Lock period");
        require(block.timestamp <= p.voteEnd + 7 days, "Expired");
        require(!p.executed, "Executed");
        
        uint256 totalVotes = p.yesVotes + p.noVotes;
        require(totalVotes > 0, "No votes");
        
        bool result = p.yesVotes > p.noVotes;
        p.executed = true;
        
        (bool success, ) = address(this).call(
            abi.encodeWithSignature("_executeProposal(bytes32)", p.proposalHash)
        );
        require(success, "Execution failed");
        
        emit ProposalExecuted(proposalId, result);
    }
}
