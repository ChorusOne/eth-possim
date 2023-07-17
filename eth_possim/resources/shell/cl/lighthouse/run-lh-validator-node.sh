#!/bin/bash

set -euo pipefail


### Consensus layer: lighthouse validators #####################################


lighthouse validator_client \
      "--beacon-nodes" "http://127.0.0.1:{{ cfg.cl.lh_node[node.index].port_api }}" \
      "--init-slashing-protection" \
      "--secrets-dir" "{{ cfg.meta.dir.cl }}/{{ node.host }}/secrets" \
      "--suggested-fee-recipient" "{{ cfg.el.funder.address }}" \
      "--testnet-dir" "{{ cfg.meta.dir.cl }}/etc" \
      "--validators-dir" "{{ cfg.meta.dir.cl }}/{{ node.host }}/validators" {% if cfg.pbs.enabled %}"--builder-proposals"{% endif %}
