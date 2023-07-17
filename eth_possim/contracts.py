import binascii
import logging
import solcx
import web3
import re


logger = logging.getLogger(__name__)


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
    tx_receipt = w3.eth.wait_for_transaction_receipt(signed_txn.hash)

    logger.info(
        f"Contract from '{path}' was published at address '{tx_receipt['contractAddress']}' [block: {tx_receipt['blockNumber']}]"
    )

    return tx_receipt["contractAddress"]
