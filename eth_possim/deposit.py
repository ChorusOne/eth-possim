import json
import re
import solcx
import time
import web3
import yaml

import eth_possim


def call_batch_deposit_contract(contract_src, *deposit_items):
    with open(".data/configuration.yaml") as f:
        cfg = yaml.safe_load(f)

    with open(contract_src, "r") as f:
        src = f.read()

    ver = ".".join(re.findall(r"pragma solidity(.+)(\d+)\.(\d+)\.(\d+)", src)[0][-3:])
    solcx.install_solc(ver)

    compiled = solcx.compile_source(
        src,
        output_values=["abi", "bin-runtime", "bin"],
        solc_version=ver,
    )
    contract = compiled[f"<stdin>:BatchDeposit"]
    abi = contract["abi"]

    contract_address = cfg["cl"]["batch_deposit_contract_address"]
    private_key = cfg["el"]["geth_node"][0]["private_key"]

    w3 = web3.Web3(
        web3.Web3.HTTPProvider(
            f"http://127.0.0.1:{cfg['el']['geth_node'][0]['port_rpc']}"
        )
    )
    # w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    contract = w3.eth.contract(
        web3.Web3.to_checksum_address(contract_address.strip()),
        abi=abi,
    )
    account = w3.eth.account.from_key(private_key)

    nonce = w3.eth.get_transaction_count(account.address)
    txn_hash = contract.functions.batchDeposit(
        [
            bytes.fromhex(deposit_item["pubkey"].replace("0x", ""))
            for deposit_item in deposit_items
        ],
        [
            bytes.fromhex(deposit_item["withdrawal_credentials"].replace("0x", ""))
            for deposit_item in deposit_items
        ],
        [
            bytes.fromhex(deposit_item["signature"].replace("0x", ""))
            for deposit_item in deposit_items
        ],
        [
            bytes.fromhex(deposit_item["deposit_data_root"].replace("0x", ""))
            for deposit_item in deposit_items
        ],
    ).transact(
        {
            "chainId": cfg["el"]["chain_id"],
            "from": web3.Web3.to_checksum_address(account.address),
            "value": w3.to_wei("64", "ether"),
            "nonce": nonce,
        }
    )

    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    return txn_receipt


def call_deposit_contract(w3, contract_abi, deposit_item):
    with open(".data/configuration.yaml") as f:
        cfg = yaml.safe_load(f)

    contract_address = cfg["cl"]["deposit_contract_address"]
    private_key = cfg["el"]["geth_node"][1]["private_key"]

    contract = w3.eth.contract(
        web3.Web3.to_checksum_address(contract_address.strip()),
        abi=contract_abi,
    )
    account = w3.eth.account.from_key(private_key)

    nonce = w3.eth.get_transaction_count(account.address)
    txn_hash = contract.functions.deposit(
        bytes.fromhex(deposit_item["pubkey"].replace("0x", "")),
        bytes.fromhex(deposit_item["withdrawal_credentials"].replace("0x", "")),
        bytes.fromhex(deposit_item["signature"].replace("0x", "")),
        bytes.fromhex(deposit_item["deposit_data_root"].replace("0x", "")),
    ).transact(
        {
            "chainId": cfg["el"]["chain_id"],
            "from": web3.Web3.to_checksum_address(account.address),
            "value": w3.to_wei("32", "ether"),
            "nonce": nonce,
        }
    )

    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    return txn_receipt


def load_initial_deposit_tree():
    with open(".data/configuration.yaml") as f:
        cfg = yaml.safe_load(f)

    with open(
        f"{eth_possim.__path__[0]}/resources/solidity/deposit-contract.sol", "r"
    ) as f:
        src = f.read()

    ver = ".".join(re.findall(r"pragma solidity(.+)(\d+)\.(\d+)\.(\d+)", src)[0][-3:])
    solcx.install_solc(ver)

    compiled = solcx.compile_source(
        src,
        output_values=["abi", "bin-runtime", "bin"],
        solc_version=ver,
    )
    contract = compiled[f"<stdin>:DepositContract"]
    abi = contract["abi"]

    with open(".data/cl/etc/initial_deposits.json") as f:
        deposit_data = json.load(f)

    w3 = web3.Web3(
        web3.Web3.HTTPProvider(
            f"http://127.0.0.1:{cfg['el']['geth_node'][1]['port_rpc']}"
        )
    )
    w3.middleware_onion.inject(
        web3.middleware.geth_poa_middleware,
        layer=0,
    )

    for deposit_item in deposit_data["deposit_data"]:
        while True:
            try:
                call_deposit_contract(
                    contract_abi=abi, deposit_item=deposit_item, w3=w3
                )
            except ValueError:
                time.sleep(0.5)
                continue
            else:
                time.sleep(3)
                break
