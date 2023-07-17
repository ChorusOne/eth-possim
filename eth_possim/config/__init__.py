from eth_possim.config.cl import initialise_cl_nodes
from eth_possim.config.el import initialise_el_nodes, initialise_genesis_json
from eth_possim.config.pbs import initialise_pbs_nodes
from eth_possim.config.renderer import render
from eth_possim.config.support import initialise_support_nodes
from eth_possim.utils import ensure_dir_exists, make_executable


def initialise_privatenet(cfg: dict):
    ensure_dir_exists(cfg["meta"]["dir"]["shell"])
    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/el/__init/init-el.sh",
        dst=f"{cfg['meta']['dir']['shell']}/init-el.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/init-el.sh")
    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/cl/__init/init-cl.sh",
        dst=f"{cfg['meta']['dir']['shell']}/init-cl.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/init-cl.sh")

    initialise_genesis_json(cfg=cfg)
    initialise_el_nodes(cfg=cfg)
    initialise_pbs_nodes(cfg=cfg)
    initialise_cl_nodes(cfg=cfg)
    initialise_support_nodes(cfg=cfg)
