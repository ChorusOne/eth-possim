import logging
import os
import sys

import click
import yaml
import eth_possim
from eth_possim.config import initialise_privatenet
from eth_possim.config.load import load_configuration
from eth_possim.config.patch import patch_cl_cfg
from eth_possim.contracts import deploy_contract_onchain
from eth_possim.deposit import load_initial_deposit_tree
from eth_possim.utils import ensure_dir_exists


# - CLI ------------------------------------------------------------------------


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--config",
    default=f"{eth_possim.__path__[0]}/resources/configuration.yaml",
    help="Path to input config file.",
    show_default=True,
)
def generate(config: str):
    """Generates basic config prior running the initialisation scripts."""
    cfg = load_configuration(
        base=f"{eth_possim.__path__[0]}/resources/configuration.yaml", src=config
    )
    ensure_dir_exists(".data/")
    with open("./.data/configuration.yaml", "w") as f:
        yaml.dump(cfg, f)
        os.fsync(f)
    initialise_privatenet(cfg=cfg)


@cli.command()
def patch_cl():
    """Patches the configuration of consensus layer."""
    with open("./.data/configuration.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    patch_cl_cfg(cfg=cfg)


@cli.command()
@click.option("--rpc", help="RPC endpoint URL address.", default="")
def deploy_batch_deposit_contract(rpc: str):
    """Deploys deposit contract on chain."""

    with open("./.data/configuration.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    if not rpc:
        rpc = f"http://localhost:{cfg['haproxy']['el']['port_geth_rpc']}"

    batch_deposit_contract_address = deploy_contract_onchain(
        cfg=cfg,
        rpc=rpc,
        path=f"{cfg['resources']}/solidity/batch-deposit-contract.sol",
        name="BatchDeposit",
        args=[
            cfg["cl"]["deposit_contract_address"],
        ],
    )

    # Patch and write back `configuration.yaml`
    cfg["cl"]["batch_deposit_contract_address"] = batch_deposit_contract_address
    with open("./.data/configuration.yaml", "w") as f:
        yaml.dump(cfg, f)


@cli.command()
@click.option("--rpc", help="RPC endpoint URL address.", default="")
@click.option("--path", help="Path to the contract source.")
@click.option("--name", help="The name of the contract.")
@click.argument("args", nargs=-1)
def deploy_contract(rpc: str, path: str, name: str, args: list):
    """Deploys any contract on chain."""
    with open("./.data/configuration.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    if not rpc:
        rpc = f"http://localhost:{cfg['haproxy']['el']['port_geth_rpc']}"
    deploy_contract_onchain(cfg=cfg, rpc=rpc, path=path, name=name, args=args)


@cli.command()
def dummy_deposit_test():
    """Deposit a lot of validators into chain, verifying eth1 works under load."""
    load_initial_deposit_tree()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    cli()
