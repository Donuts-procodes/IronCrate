// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title  IronCrateRegistry
/// @notice Immutable on-chain log of vehicular incident video hashes.
/// @dev    Deploy on Polygon Amoy testnet. Paste address into backend/.env
contract IronCrateRegistry {

    event IncidentLogged(
        address indexed reporter,
        bytes32 indexed videoHash,
        uint256 timestamp
    );

    struct IncidentRecord {
        address reporter;
        bytes32 videoHash;
        string  metadataJson;
        uint256 timestamp;
    }

    IncidentRecord[] public incidents;
    mapping(address => uint256[]) public incidentsByReporter;

    function logIncident(bytes32 videoHash, string calldata metadataJson) external {
        require(videoHash != bytes32(0), "IronCrate: hash required");

        uint256 id = incidents.length;
        incidents.push(IncidentRecord({
            reporter:     msg.sender,
            videoHash:    videoHash,
            metadataJson: metadataJson,
            timestamp:    block.timestamp
        }));
        incidentsByReporter[msg.sender].push(id);
        emit IncidentLogged(msg.sender, videoHash, block.timestamp);
    }

    function getIncident(uint256 id) external view returns (IncidentRecord memory) {
        require(id < incidents.length, "IronCrate: not found");
        return incidents[id];
    }

    function totalIncidents() external view returns (uint256) {
        return incidents.length;
    }

    function incidentsOf(address reporter) external view returns (uint256[] memory) {
        return incidentsByReporter[reporter];
    }
}
