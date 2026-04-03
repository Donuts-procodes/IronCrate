"""
IronCrate - Crypto & Blockchain Core
SHA-256 hashing + Polygon Amoy anchoring via Web3.
"""

import hashlib, json, os, time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL          = os.getenv("POLYGON_RPC_URL", "https://rpc-amoy.polygon.technology")
PRIVATE_KEY      = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "videoHash",     "type": "bytes32"},
            {"internalType": "string",  "name": "metadataJson",  "type": "string"},
        ],
        "name": "logIncident",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "getIncident",
        "outputs": [
            {"internalType": "address", "name": "reporter",     "type": "address"},
            {"internalType": "bytes32", "name": "videoHash",    "type": "bytes32"},
            {"internalType": "string",  "name": "metadataJson", "type": "string"},
            {"internalType": "uint256", "name": "timestamp",    "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


def hash_bytes(data: bytes) -> str:
    """Return hex SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_file(path: str) -> str:
    """Return hex SHA-256 digest of a file (chunked for large files)."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _get_contract():
    if not PRIVATE_KEY or not CONTRACT_ADDRESS:
        raise ValueError("PRIVATE_KEY and CONTRACT_ADDRESS must be set in .env")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to RPC: {RPC_URL}")
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=CONTRACT_ABI,
    )
    return w3, contract


def sign_and_anchor(video_hash: str, metadata: dict, video_url: str = "") -> str:
    """
    Anchor a video SHA-256 hash on Polygon Amoy.
    Returns the transaction hash string.
    """
    w3, contract = _get_contract()
    account = w3.eth.account.from_key(PRIVATE_KEY)

    meta_json = json.dumps({
        **metadata,
        "video_url": video_url,
        "anchored_at": int(time.time()),
    })

    hash_bytes32 = bytes.fromhex(video_hash)

    tx = contract.functions.logIncident(hash_bytes32, meta_json).build_transaction({
        "from":     account.address,
        "nonce":    w3.eth.get_transaction_count(account.address),
        "gas":      200_000,
        "gasPrice": w3.to_wei("30", "gwei"),
    })

    signed  = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    if receipt.status != 1:
        raise RuntimeError("Transaction reverted on-chain.")

    return tx_hash.hex()


def get_tx_status(tx_hash: str) -> dict:
    w3, _ = _get_contract()
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    if receipt is None:
        return {"status": "pending"}
    return {
        "status":       "success" if receipt.status == 1 else "failed",
        "block_number": receipt.blockNumber,
        "gas_used":     receipt.gasUsed,
    }


def get_incident_from_chain(tx_hash: str) -> dict:
    """Fetch raw tx input data for verification."""
    w3, _ = _get_contract()
    tx = w3.eth.get_transaction(tx_hash)
    return {
        "from":        tx["from"],
        "block":       tx.get("blockNumber"),
        "gas_price":   str(tx.get("gasPrice")),
    }
