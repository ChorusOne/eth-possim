import binascii
import json
import logging
import solcx
import web3
import re
import time
from typing import List, Tuple
from web3.types import TxReceipt, HexStr


logger = logging.getLogger(__name__)

def wait_for_transaction_receipt(w3: web3.Web3, signed_txn_hash: HexStr) -> TxReceipt:
    for _ in range(1, 100):
        try:
            tx_receipt = w3.eth.wait_for_transaction_receipt(signed_txn_hash)
            return tx_receipt
        except ValueError as exc:
            if exc.args[0]["message"] == "transaction indexing is in progress":
                logger.info(
                    "Failed to get transaction receipt due to indexing, will retry"
                )
                time.sleep(5)
                continue
            else:
                raise

def deploy_compiled_contract(
    cfg: dict,
    rpc: str,
    foundry_json_path: str,
    args: list = [],
    libraries: List[Tuple[str, str]] = [],
) -> str:
    with open(foundry_json_path, "r") as f:
        foundry_json = json.loads(f.read())

    bytecode_str = foundry_json["bytecode"]["object"][2:]
    for library in libraries:
        # Skip 0x from the library address.
        bytecode_str = bytecode_str.replace(library[0], library[1][2:])
    bytecode = binascii.unhexlify(bytecode_str)

    abi = foundry_json["abi"]

    w3 = web3.Web3(web3.Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(
        web3.middleware.geth_poa_middleware,
        layer=0,
    )

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    account = w3.eth.account.from_key(cfg["el"]["funder"]["private_key"])
    w3.eth.default_account = account
    nonce = w3.eth.get_transaction_count(account.address)

    deploy_tx = contract.constructor(*args).build_transaction(
        {
            "chainId": cfg["el"]["chain_id"],
            # "gas": Let the function estimate gas.
            # "gasPrice": Let the function estimate gas price.
            "from": account.address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(
        deploy_tx,
        private_key=cfg["el"]["funder"]["private_key"],
    )
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    tx_receipt = wait_for_transaction_receipt(w3, signed_txn.hash)
    logger.info(f"Contract from '{foundry_json_path}' was published at address '{tx_receipt['contractAddress']}' [block: {tx_receipt['blockNumber']}]")
    return tx_receipt["contractAddress"]


def deploy_contract_onchain(
    cfg: dict, rpc: str, path: str, name: str, args: list = []
) -> str:
    with open(path, "r") as f:
        src = f.read()
    ver = ".".join(re.findall(r"pragma solidity(.+)(\d+)\.(\d+)\.(\d+)", src)[0][-3:])
    solcx.install_solc(ver)

    compiled = solcx.compile_source(
        src,
        output_values=["abi", "bin-runtime", "bin"],
        solc_version=ver,
    )
    contract = compiled[f"<stdin>:{name}"]
    bytecode = binascii.unhexlify(contract["bin"])
    abi = contract["abi"]

    w3 = web3.Web3(web3.Web3.HTTPProvider(rpc))
    w3.middleware_onion.inject(
        web3.middleware.geth_poa_middleware,
        layer=0,
    )

    deposit = w3.eth.contract(abi=abi, bytecode=bytecode)
    account = w3.eth.account.from_key(cfg["el"]["funder"]["private_key"])
    w3.eth.default_account = account
    nonce = w3.eth.get_transaction_count(account.address)

    deploy_tx = deposit.constructor(*args).build_transaction(
        {
            "chainId": cfg["el"]["chain_id"],
            # "gas": Let the function estimate gas.
            # "gasPrice": Let the function estimate gas price.
            "from": account.address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(
        deploy_tx,
        private_key=cfg["el"]["funder"]["private_key"],
    )
    w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = wait_for_transaction_receipt(w3, signed_txn.hash)

    logger.info(
        f"Contract from '{path}' was published at address '{tx_receipt['contractAddress']}' [block: {tx_receipt['blockNumber']}]"
    )

    return tx_receipt["contractAddress"]
