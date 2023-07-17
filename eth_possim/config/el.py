import binascii
import json
import logging
import os
import secrets
import shutil
import time
import tomlkit
import web3

from eth_possim.config.renderer import render, render_with_node
from eth_possim.utils import ensure_dir_exists, ensure_key_exists, make_executable


logger = logging.getLogger(__name__)


def initialise_genesis_json(cfg: dict):
    with open(f"{cfg['resources']}/el/genesis.json", "r") as f:
        genesis = json.load(f)
        logging.debug(f"Loaded genesis file from '{os.path.abspath(f.name)}'")

    base = cfg["meta"]["dir"]["el"]
    ensure_dir_exists(f"{base}/etc")

    nodes = cfg["el"]["geth_node"]

    # Assign balances
    ensure_key_exists(genesis, "alloc")
    funder_address = cfg["el"]["funder"]["address"]
    ensure_key_exists(genesis["alloc"], funder_address)
    genesis["alloc"][funder_address]["balance"] = cfg["el"]["funder"]["balance"]
    for node in nodes:
        address = web3.Web3.to_checksum_address(node["address"])
        ensure_key_exists(genesis["alloc"], address)
        genesis["alloc"][address]["balance"] = node["balance"]

    # Update chain ID/name
    ensure_key_exists(genesis, "config")
    genesis["config"]["chainId"] = cfg["el"]["chain_id"]
    genesis["config"]["chainName"] = cfg["el"]["chain_name"]

    # Update Shanghai fork time
    # genesis["shanghaiTime"] = cfg["el"]["override_shanghai"]

    # Update eth1 genesis timestamp
    genesis["timestamp"] = (
        int(time.time())
        - cfg["cl"]["seconds_per_eth1_block"] * (cfg["cl"]["slots_per_epoch"])
        + 1
    )

    with open(f"{base}/etc/genesis.json", "w") as f:
        json.dump(genesis, f, indent=2, sort_keys=True)
        logging.debug(f"Created a genesis file at '{os.path.abspath(f.name)}'")


def initialise_el_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["el"]
    ensure_dir_exists(base)
    _initialise_geth_and_mev_nodes(cfg=cfg)


def _initialise_geth_and_mev_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["el"]

    # Initialize boot node
    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/el/geth/run-el-bootnode.sh",
        dst=f"{cfg['meta']['dir']['shell']}/run-el-bootnode.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/run-el-bootnode.sh")

    if cfg["pbs"]["enabled"]:
        nodes = cfg["el"]["geth_node"] + cfg["el"]["mev_builder_node"]
    else:
        nodes = cfg["el"]["geth_node"]

    for node in nodes:
        host = node["host"]
        node_base = f"{base}/{host}"
        ensure_dir_exists(node_base)

        # Render and "fix" `config.toml`
        render_with_node(
            cfg=cfg,
            node=node,
            src=f"{cfg['resources']}/el/config.toml",
            dst=f"{node_base}/config.toml",
        )
        with open(f"{node_base}/config.toml", "r") as f:
            config_toml = tomlkit.load(f)
            logging.debug(
                f"Loaded current geth configuration from '{os.path.abspath(f.name)}'"
            )
        # To silence the linter on the template for `config.toml` we
        # make `MaxPeers` to be a string there.  However, geth wants it
        # to be `int`.
        config_toml["Node"]["P2P"]["MaxPeers"] = int(
            config_toml["Node"]["P2P"]["MaxPeers"]
        )
        with open(f"{node_base}/config.toml", "w") as f:
            tomlkit.dump(config_toml, f)
            logging.debug(
                f"Updated current geth configuration at '{os.path.abspath(f.name)}'"
            )

        keystore_base = f"{node_base}/keystore"
        keystore_file = f"{keystore_base}/{node['keystore']}"
        ensure_dir_exists(keystore_base)
        shutil.copy(
            src=f"{cfg['resources']}/el/{host}.json",
            dst=keystore_file,
        )
        logging.info(f"Created keystore at '{keystore_file}'")

    for node in cfg["el"]["geth_node"]:
        # Render execution node wrapper script
        render_with_node(
            cfg=cfg,
            node=node,
            src=f"{cfg['resources']}/shell/el/geth/run-geth-node.sh",
            dst=f"{cfg['meta']['dir']['shell']}/run-geth-node-{node['index']}.sh",
        )
        make_executable(
            f"{cfg['meta']['dir']['shell']}/run-geth-node-{node['index']}.sh"
        )

    if cfg["pbs"]["enabled"]:
        for node in cfg["el"]["mev_builder_node"]:
            # Render MEV node wrapper script
            render_with_node(
                cfg=cfg,
                node=node,
                src=f"{cfg['resources']}/shell/pbs/run-mev-builder.sh",
                dst=f"{cfg['meta']['dir']['shell']}/run-mev-builder-{node['index']}.sh",
            )
            make_executable(
                f"{cfg['meta']['dir']['shell']}/run-mev-builder-{node['index']}.sh"
            )

    with open(f"{base}/etc/jwt-secret.txt", "w") as f:
        secret = binascii.hexlify(secrets.token_bytes(32)).decode("utf-8")
        f.write(secret)
        logging.info(f"Generated JWT secret in '{os.path.abspath(f.name)}'")

    with open(f"{base}/etc/signer-password.txt", "w") as f:
        password = cfg["el"]["signer_password"]
        f.write(password)
        logging.info(f"Generated signer password in '{os.path.abspath(f.name)}'")
