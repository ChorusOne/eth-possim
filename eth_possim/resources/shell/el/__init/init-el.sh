#!/bin/bash

set -euxo pipefail

### Execution layer: geth ######################################################

  # {%- for node in cfg.el.geth_node %}

geth init --datadir {{ cfg.meta.dir.el }}/geth-{{ node.index }} {{ cfg.meta.dir.el }}/etc/genesis.json


  # {%- endfor %}

### Execution layer: mev-builder ###############################################

  # {%- for idx in range(cfg.cl.mev_prysm_node_count) %}
  # {%- set node = cfg.el.mev_builder_node[idx] %}
geth init --datadir {{ cfg.meta.dir.el }}/mev-builder-{{ node.index }} {{ cfg.meta.dir.el }}/etc/genesis.json

  # {%- endfor %}
