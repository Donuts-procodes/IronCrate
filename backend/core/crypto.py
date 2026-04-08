"""
IronCrate — core/crypto.py
SHA-256 hashing helpers and Polygon Amoy blockchain anchoring via Web3.py.
"""
import os
import json
import hashlib
from web3 import Web3

# ── ABI (minimal — only what we call) ────────────────────────────────────────
_ABI = json.loads('[{"inputs":[{"internalType":"bytes32","name":"videoHash","type":"bytes32"},{"internalType":"string","name":"metadataJson","type":"string"}],"name":"logIncident","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"id","type":"uint256"}],"name":"getIncident","outputs":[{"components":[{"internalType":"address","name":"reporter","type":"address"},{"internalType":"bytes32","name":"videoHash","type":"bytes32"},{"internalType":"string","name":"metadataJson","type":"string"},{"internalType":"uint256","name":"timestamp","type":"uint256"}],"internalType":"struct IronCrateRegistry.IncidentRecord","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalIncidents","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"reporter","type":"address"},{"indexed":true,"internalType":"bytes32","name":"videoHash","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"IncidentLogged","type":"event"}]')


def _get_web3():
    rpc = os.getenv("POLYGON_RPC_URL")
    if not rpc:
        raise EnvironmentError("POLYGON_RPC_URL is not set in .env")
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {rpc}")
    return w3


def _get_contract(w3):
    addr = os.getenv("CONTRACT_ADDRESS")
    if not addr or addr == "0xYourDeployedContractAddressHere":
        raise EnvironmentError(
            "CONTRACT_ADDRESS is not set. Deploy IronCrateRegistry.sol first."
        )
    return w3.eth.contract(address=Web3.to_checksum_address(addr), abi=_ABI)


def hash_file(filepath: str) -> str:
    """Return the hex SHA-256 digest of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_bytes(data: bytes) -> str:
    """Return the hex SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sign_and_anchor(video_hash: str, metadata: dict, video_url: str) -> str:
    """
    Anchor *video_hash* on the Polygon Amoy chain via IronCrateRegistry.
    Returns the transaction hash as a hex string.
    Raises EnvironmentError if CONTRACT_ADDRESS is not configured.
    """
    w3       = _get_web3()
    contract = _get_contract(w3)

    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise EnvironmentError("PRIVATE_KEY is not set in .env")

    account    = w3.eth.account.from_key(private_key)
    hash_bytes32 = bytes.fromhex(video_hash)

    metadata_json = json.dumps({**metadata, "video_url": video_url})

    nonce = w3.eth.get_transaction_count(account.address)
    tx    = contract.functions.logIncident(hash_bytes32, metadata_json).build_transaction({
        "from":     account.address,
        "nonce":    nonce,
        "gas":      300_000,
        "gasPrice": w3.eth.gas_price,
    })

    signed  = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()


def get_tx_status(tx_hash: str) -> dict:
    """Return receipt info for a submitted transaction."""
    w3      = _get_web3()
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    if receipt is None:
        return {"status": "pending", "tx_hash": tx_hash}
    return {
        "status":       "success" if receipt.status == 1 else "failed",
        "tx_hash":      tx_hash,
        "block_number": receipt.blockNumber,
        "gas_used":     receipt.gasUsed,
    }
