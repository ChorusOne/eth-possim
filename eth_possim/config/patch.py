import logging
import os
import shutil
import yaml

from eth_possim.utils import ensure_dir_exists, hexes_as_hexes, hexes_as_strings


logger = logging.getLogger(__name__)


def patch_cl_cfg(cfg: dict):
    _patch_cl_config_yaml(cfg=cfg)
    _patch_cl_lh_nodes(cfg=cfg)


def _patch_cl_config_yaml(cfg: dict):
    """
    Patches CL `config.yaml` after it has been pre-processed by `lcli`.

    Firstly, `lcli` drops some of the parameters we specify in
    `privatenet.yaml`.  So, we have to put them back.  Also, since lh/teku want
    hexadecimals to be strings (otherwise one of them fails to parse YAML
    because of int64 overflow), we must make sure that all hexes are wrapped in
    quotes.

    Secondly, `prysm` actually wants hexes to be hexes.  Which is why we have to
    unwrap them from quotes.
    """

    # Load original minimal spec
    with open(f"{cfg['resources']}/cl/minimal.yaml", "r") as f:
        minimal_yaml = yaml.safe_load(hexes_as_strings(f.read()))
        logging.debug(
            f"Loaded minimal preset configuration from '{os.path.abspath(f.name)}'"
        )
    # Load `config.yaml` that `lcli` had produced
    with open(f"{cfg['meta']['dir']['cl']}/etc/config.yaml", "r") as f:
        lcli_yaml = yaml.safe_load(hexes_as_strings(f.read()))
        logging.debug(
            f"Loaded current CL configuration from '{os.path.abspath(f.name)}'"
        )
    # Load our privatenet parameters
    with open(f"{cfg['resources']}/cl/privatenet.yaml", "r") as f:
        privatenet_yaml = yaml.safe_load(hexes_as_strings(f.read()))
        logging.debug(
            f"Loaded privatenet configuration from '{os.path.abspath(f.name)}'"
        )

    # Merge: privatenet -> lcli -> minimal
    res_yaml = minimal_yaml
    for k, v in lcli_yaml.items():
        res_yaml[k] = v
    for k, v in privatenet_yaml.items():
        res_yaml[k] = v

    # Write back
    with open(f"{cfg['meta']['dir']['cl']}/etc/config.yaml", "w") as f:
        yaml.dump(res_yaml, f, indent=2)
        logging.info(f"Patched CL configuration at '{os.path.abspath(f.name)}'")

    # prysm --------------------------------------------------------------------

    # Prysm prefers numbers as numbers (without quotes)
    for k in res_yaml:
        v = res_yaml[k]
        try:
            v = int(v)
            res_yaml[k] = v
        except ValueError:
            pass
    # ... and hexes as hexes (also without quotes)
    confg_prysm_yaml = hexes_as_hexes(yaml.dump(res_yaml))
    with open(f"{cfg['meta']['dir']['cl']}/etc/config-prysm.yaml", "w") as f:
        f.write(confg_prysm_yaml)
        logging.info(
            f"Created prysm-compatible CL configuration at '{os.path.abspath(f.name)}'"
        )


def _patch_cl_lh_nodes(cfg: dict):
    base = cfg["meta"]["dir"]["cl"]
    for node in cfg["cl"]["lh_val"]:
        ensure_dir_exists(f"{base}/{node['host']}")
    for node in cfg["cl"]["lh_node"]:
        index = int(node["index"])
        shutil.move(
            f"{base}/node_{index + 1}/secrets",
            f"{base}/{cfg['cl']['lh_val'][index]['host']}/secrets",
        )
        shutil.move(
            f"{base}/node_{index + 1}/validators",
            f"{base}/{cfg['cl']['lh_val'][index]['host']}/validators",
        )
        shutil.move(
            f"{base}/node_{index + 1}",
            f"{base}/{node['host']}",
        )
