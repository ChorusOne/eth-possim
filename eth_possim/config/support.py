from eth_possim.config.renderer import render
from eth_possim.utils import ensure_dir_exists, make_executable


def initialise_support_nodes(cfg: dict):
    haproxy_base = cfg["meta"]["dir"]["haproxy"]
    ensure_dir_exists(haproxy_base)

    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/net/run-haproxy-el.sh",
        dst=f"{cfg['meta']['dir']['shell']}/run-haproxy-el.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/run-haproxy-el.sh")
    render(
        cfg=cfg,
        src=f"{cfg['resources']}/haproxy/el.cfg",
        dst=f"{haproxy_base}/el.cfg",
    )

    render(
        cfg=cfg,
        src=f"{cfg['resources']}/shell/net/run-haproxy-cl.sh",
        dst=f"{cfg['meta']['dir']['shell']}/run-haproxy-cl.sh",
    )
    make_executable(f"{cfg['meta']['dir']['shell']}/run-haproxy-cl.sh")
    render(
        cfg=cfg,
        src=f"{cfg['resources']}/haproxy/cl.cfg",
        dst=f"{haproxy_base}/cl.cfg",
    )
