#!/bin/bash

set -euo pipefail

### Consensus layer: lighthouse beacons ########################################

lighthouse beacon_node \
    "--datadir" "{{ cfg.meta.dir.cl }}/{{ node.host }}" \
    "--debug-level" "{{ cfg.cl.debug_level }}" \
    "--disable-packet-filter" \
    "--disable-upnp" \
    "--enable-private-discovery" \
    "--disable-peer-scoring" \
    "--disable-enr-auto-update" \
    "--enr-address" "127.0.0.1" \
    "--discovery-port" "{{ node.port_p2p }}" \
    "--enr-udp-port" "{{ node.port_p2p }}" \
    "--enr-tcp-port" "{{ node.port_p2p }}" \
    "--execution-endpoint" "http://127.0.0.1:{{ cfg.el.geth_node[node.index].port_arpc }}" \
    "--execution-jwt" "{{ cfg.meta.dir.el }}/etc/jwt-secret.txt" \
    "--graffiti" "{{ node.host }}" \
    "--http-address" "127.0.0.1" \
    "--http-allow-origin" '*' \
    "--http-port" "{{ node.port_api }}" \
    "--http-allow-sync-stalled" \
    "--http" {% if cfg.pbs.enabled -%}"--builder" "http://127.0.0.1:{{ cfg.cl.mev_boost.port_api }}" "--always-prefer-builder-payload" {% endif -%}\
    "--port" "{{ node.port_p2p }}" \
    "--staking" \
    "--subscribe-all-subnets" \
    "--import-all-attestations" \
    "--target-peers" "{{ cfg.cl.lh_node_count + cfg.cl.teku_node_count + cfg.cl.mev_prysm_node_count - 1 }}" \
    "--testnet-dir" "{{ cfg.meta.dir.cl }}/etc" \
    "--logfile" "{{ cfg.meta.dir.cl }}/{{ node.host }}/beacon-node.log" \
    "--logfile-no-restricted-perms" \
    "--disable-optimistic-finalized-sync"
