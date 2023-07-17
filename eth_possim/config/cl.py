import shutil

from eth_possim.config.renderer import render, render_with_node
from eth_possim.utils import ensure_dir_exists, make_executable


def initialise_cl_nodes(cfg: dict):
    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/cl/__init/eth2-genesis.sh",
        dst=f"{cfg['meta']['dir']['shell']}/eth2-genesis.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/eth2-genesis.sh")

    _initialise_lh_nodes(cfg=cfg)
    _initialise_teku_nodes(cfg=cfg)
    _initialise_mev_prysm_nodes(cfg=cfg)


def _initialise_lh_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["cl"]
    ensure_dir_exists(f"{base}/etc")

    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/cl/lighthouse/run-lh-boot.sh",
        dst=f"{cfg['meta']['dir']['shell']}/run-lh-boot.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/run-lh-boot.sh")

    shutil.copy(
        f"{cfg['resources']}/cl/initial_deposits.json",
        f"{base}/etc/initial_deposits.json",
    )

    for lh_beacon_node in cfg["cl"]["lh_node"]:
        render_with_node(
            cfg=cfg,
            node=lh_beacon_node,
            src=f"{cfg['resources']}/shell/cl/lighthouse/run-lh-beacon-node.sh",
            dst=f"{cfg['meta']['dir']['shell']}/run-lh-beacon-node-{lh_beacon_node['index']}.sh",
        )
        make_executable(
            f"{cfg['meta']['dir']['shell']}/run-lh-beacon-node-{lh_beacon_node['index']}.sh"
        )

    for lh_val_node in cfg["cl"]["lh_val"]:
        render_with_node(
            cfg=cfg,
            node=lh_val_node,
            src=f"{cfg['resources']}/shell/cl/lighthouse/run-lh-validator-node.sh",
            dst=f"{cfg['meta']['dir']['shell']}/run-lh-validator-node-{lh_val_node['index']}.sh",
        )
        make_executable(
            f"{cfg['meta']['dir']['shell']}/run-lh-validator-node-{lh_val_node['index']}.sh"
        )


def _initialise_teku_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["cl"]
    for node in cfg["cl"]["teku_node"]:
        ensure_dir_exists(f"{base}/{node['host']}")
        render_with_node(
            cfg=cfg,
            node=node,
            src=f"{cfg['resources']}/shell/cl/teku/run-teku-beacon-node.sh",
            dst=f"{cfg['meta']['dir']['shell']}/run-teku-beacon-node-{node['index']}.sh",
        )
        make_executable(
            f"{cfg['meta']['dir']['shell']}/run-teku-beacon-node-{node['index']}.sh"
        )


def _initialise_mev_prysm_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["cl"]
    for node in cfg["cl"]["mev_prysm_node"]:
        ensure_dir_exists(f"{base}/{node['host']}")

        render_with_node(
            cfg=cfg,
            node=node,
            src=f"{cfg['resources']}/shell/pbs/run-mev-prysm.sh",
            dst=f"{cfg['meta']['dir']['shell']}/run-mev-prysm-{node['index']}.sh",
        )
        make_executable(
            f"{cfg['meta']['dir']['shell']}/run-mev-prysm-{node['index']}.sh"
        )
