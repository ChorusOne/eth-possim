from eth_possim.config.renderer import render, render_with_node
from eth_possim.utils import ensure_dir_exists, make_executable


def initialise_pbs_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["cl"]
    mev_relay_node = cfg["cl"]["mev_relay"]
    ensure_dir_exists(f"{base}/{mev_relay_node['host']}")

    render_with_node(
        cfg=cfg,
        node=mev_relay_node,
        src=f"{cfg['resources']}/shell/pbs/run-mev-relay.sh",
        dst=f"{cfg['meta']['dir']['shell']}/run-mev-relay.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/run-mev-relay.sh")

    mev_boost_node = cfg["cl"]["mev_boost"]

    render_with_node(
        cfg=cfg,
        node=mev_boost_node,
        src=f"{cfg['resources']}/shell/pbs/run-mev-boost.sh",
        dst=f"{cfg['meta']['dir']['shell']}/run-mev-boost.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/run-mev-boost.sh")
