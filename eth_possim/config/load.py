import logging
import os
import time
import yaml

from eth_possim.utils import ensure_key_exists, hexes_as_strings


_BASE_PORT_EL_BOOT = 30000
_BASE_PORT_GETH = 31000
_BASE_PORT_MEV_BUILDER = 32000
_BASE_PORT_LH = 33000
_BASE_PORT_TEKU = 34000
_BASE_PORT_MEV_PRYSM = 36000
_BASE_PORT_MEV_RELAY = 37000
_BASE_PORT_MEV_BOOST = 38000

logger = logging.getLogger(__name__)


# https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (
            k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict)
        ):  # noqa
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def load_configuration(src: str, base: str) -> dict:
    with open(base, "r") as f:
        cfg = yaml.safe_load(f)

    if src != base:
        with open(src, "r") as f:
            dict_merge(cfg, yaml.safe_load(f))

    # Inject meta
    cwd = os.path.abspath(os.curdir)
    cfg["resources"] = os.path.join(
        os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "resources"
    )
    cfg["meta"] = {
        "gcr": "eu.gcr.io/chorus-one-devops",
        "gid": os.getgid(),
        "uid": os.getuid(),
        "dir": {
            "base": cwd,
            "cl": f"{cwd}/.data/cl",
            "el": f"{cwd}/.data/el",
            "haproxy": f"{cwd}/.data/haproxy",
            "shell": f"{cwd}/.data/shell",
            "pbs": f"{cwd}/.data/pbs",
        },
    }

    # Process PBS enablement to build mev_builder_nodes
    if not cfg["pbs"]["enabled"]:
        cfg["cl"]["mev_prysm_node_count"] = 0
    else:
        cfg["cl"]["mev_prysm_node_count"] = 1

    # Configure CL to initialize target genesis timestamp
    _configure_cl(cfg=cfg)

    # Configure timestamps
    _set_timestamps(cfg=cfg)

    # Configure the nodes
    _configure_geth_nodes(cfg=cfg)
    _configure_mev_builder_nodes(cfg=cfg)
    _configure_mev_boost_and_relay(cfg=cfg)

    _configure_lh_boot_node(cfg=cfg)
    _configure_lh_nodes(cfg=cfg)
    _configure_teku_nodes(cfg=cfg)
    _configure_mev_prysm_nodes(cfg=cfg)
    _configure_lh_val_nodes(cfg=cfg)
    _configure_support_nodes(cfg=cfg)

    logging.debug(f"Loaded and updated '{os.path.abspath(f.name)}'")
    return cfg


def _set_timestamps(cfg: dict):
    now = time.time()
    genesis = now + cfg["cl"]["genesis_delay"]

    cfg["cl"]["min_genesis_time"] = int(now)
    cfg["cl"]["genesis_time"] = int(genesis)

    capella_fork_epoch = cfg["cl"]["capella_fork_epoch"]
    slots_per_epoch = cfg["cl"]["slots_per_epoch"]
    seconds_per_slot = cfg["cl"]["seconds_per_slot"]

    cfg["el"]["override_shanghai"] = int(
        genesis
        + capella_fork_epoch * slots_per_epoch * seconds_per_slot
        + cfg["cl"]["genesis_delay"]
    )


def _configure_geth_nodes(cfg: dict):
    geth_node_count = cfg["cl"]["lh_node_count"] + cfg["cl"]["teku_node_count"]
    cfg["el"]["bootnode"] = {"port_rpc": _BASE_PORT_EL_BOOT}
    cfg["el"]["geth_node_count"] = geth_node_count
    for index in range(geth_node_count):
        node = cfg["el"]["geth_node"][index]
        for k, v in {
            "host": f"geth-{index}",
            "index": index,
            "port_p2p": _BASE_PORT_GETH + index * 10 + 0,  # default 30303
            "port_rpc": _BASE_PORT_GETH + index * 10 + 1,  # default 8545
            "port_arpc": _BASE_PORT_GETH + index * 10 + 2,  # default 8551
            "port_wsrpc": _BASE_PORT_GETH + index * 10 + 3,  # default 8546
        }.items():
            node[k] = v


def _configure_mev_builder_nodes(cfg: dict):
    mev_builder_node_count = cfg["cl"]["mev_prysm_node_count"]
    cfg["el"]["mev_builder_node_count"] = mev_builder_node_count
    for index in range(mev_builder_node_count):
        node = cfg["el"]["mev_builder_node"][index]
        for k, v in {
            "host": f"mev-builder-{index}",
            "index": index,
            "port_p2p": _BASE_PORT_MEV_BUILDER + index * 10 + 0,  # default 30303
            "port_rpc": _BASE_PORT_MEV_BUILDER + index * 10 + 1,  # default 8545
            "port_arpc": _BASE_PORT_MEV_BUILDER + index * 10 + 2,  # default 8551
            "port_wsrpc": _BASE_PORT_MEV_BUILDER + index * 10 + 3,  # default 8546
            "port_builder": _BASE_PORT_MEV_BUILDER + index * 10 + 4,  # default 8546
        }.items():
            node[k] = v


def _configure_mev_boost_and_relay(cfg: dict):
    cfg["cl"]["mev_relay"] = {
        "port_relay": _BASE_PORT_MEV_RELAY,
        "port_api": _BASE_PORT_MEV_RELAY + 1,
        "host": "mev-relay",
    }
    cfg["cl"]["mev_boost"] = {
        "port_api": _BASE_PORT_MEV_BOOST,
        "host": "mev-boost",
    }


def _configure_cl(cfg: dict):
    # Read from config files
    with open(f"{cfg['resources']}/cl/minimal.yaml", "r") as f:
        minimal_yaml = yaml.safe_load(hexes_as_strings(f.read()))
        logging.debug(
            f"Loaded `minimal` CL configuration from '{os.path.abspath(f.name)}'"
        )
    with open(f"{cfg['resources']}/cl/privatenet.yaml", "r") as f:
        privatenet_yaml = yaml.safe_load(hexes_as_strings(f.read()))
        logging.debug(
            f"Loaded `privatenet` CL configuration from '{os.path.abspath(f.name)}'"
        )
    # Merge into `cfg`
    for k, v in minimal_yaml.items():
        cfg["cl"][k.lower()] = v
    for k, v in privatenet_yaml.items():
        cfg["cl"][k.lower()] = v


def _configure_lh_boot_node(cfg: dict):
    ensure_key_exists(cfg["cl"], "lh_boot")
    cfg["cl"]["lh_boot"] = {
        "host": "lh-boot",
        "port": 9000,  # default 9000
    }


def _configure_lh_nodes(cfg: dict):
    cfg["cl"]["lh_node"] = []
    for index in range(cfg["cl"]["lh_node_count"]):
        cfg["cl"]["lh_node"].append(
            {
                "host": f"lh-{index}",
                "index": index,
                "port_p2p": _BASE_PORT_LH + index * 10 + 0,  # default 9000
                "port_api": _BASE_PORT_LH + index * 10 + 1,  # default 5052
            }
        )


def _configure_teku_nodes(cfg: dict):
    cfg["cl"]["teku_node"] = []
    for index in range(cfg["cl"]["teku_node_count"]):
        cfg["cl"]["teku_node"].append(
            {
                "host": f"teku-{index}",
                "index": index,
                "port_p2p": _BASE_PORT_TEKU + index * 10 + 0,  # default 9000
                "port_api": _BASE_PORT_TEKU + index * 10 + 1,  # default 5051
            }
        )


def _configure_mev_prysm_nodes(cfg: dict):
    cfg["cl"]["mev_prysm_node_count"] = cfg["el"]["mev_builder_node_count"]
    cfg["cl"]["mev_prysm_node"] = []
    for index in range(cfg["cl"]["mev_prysm_node_count"]):
        cfg["cl"]["mev_prysm_node"].append(
            {
                "host": f"mev-prysm-{index}",
                "index": index,
                "port_p2p": _BASE_PORT_MEV_PRYSM
                + index * 10
                + 0,  # default 13000/12000
                "port_rpc": _BASE_PORT_MEV_PRYSM + index * 10 + 1,  # default 4000
                "port_api": _BASE_PORT_MEV_PRYSM + index * 10 + 2,  # default 3500
            }
        )


def _configure_lh_val_nodes(cfg: dict):
    cfg["cl"]["lh_val"] = []
    for index in range(cfg["cl"]["lh_node_count"]):
        cfg["cl"]["lh_val"].append(
            {
                "host": f"lh-val-{index}",
                "index": index,
            }
        )


def _configure_support_nodes(cfg: dict):
    # HAProxy
    cfg["haproxy"] = {
        "el": {
            "host": "haproxy-el",
            "port_geth_rpc": cfg["port"]["geth_rpc"],
            "port_geth_wsrpc": cfg["port"]["geth_wsrpc"],
            "health_check": {
                "geth": os.path.abspath(
                    f"{cfg['meta']['dir']['haproxy']}/scripts/healthcheck-geth.sh"
                ),
            },
        },
        "cl": {
            "host": "haproxy-cl",
            "port_api": cfg["port"]["beacon_api"],
            "port_lh_api": cfg["port"]["lh_api"],
            "port_teku_api": cfg["port"]["teku_api"],
            "health_check": {
                "beacon": os.path.abspath(
                    f"{cfg['meta']['dir']['haproxy']}/scripts/healthcheck-cl.sh"
                ),
                "lighthouse": os.path.abspath(
                    f"{cfg['meta']['dir']['haproxy']}/scripts/healthcheck-lh.sh"
                ),
                "teku": os.path.abspath(
                    f"{cfg['meta']['dir']['haproxy']}/scripts/healthcheck-teku.sh"
                ),
            },
        },
    }
