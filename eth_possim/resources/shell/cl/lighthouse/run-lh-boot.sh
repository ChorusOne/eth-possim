#!/bin/bash

set -euo pipefail

### Consensus layer: lighthouse boot node ######################################


lighthouse boot_node \
    "--datadir" "{{ cfg.meta.dir.cl }}/boot" \
    "--disable-packet-filter" \
    "--network-dir" "{{ cfg.meta.dir.cl }}/boot/enr" \
    "--port" "{{ cfg.cl.lh_boot.port }}" \
    "--testnet-dir" "{{ cfg.meta.dir.cl }}/etc"
