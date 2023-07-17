#!/bin/bash

set -exuo pipefail

### Execution layer: geth ######################################################

geth \
    "--allow-insecure-unlock" \
    "--authrpc.addr"   "0.0.0.0"   \
    "--authrpc.jwtsecret"   "{{ cfg.meta.dir.el }}/etc/jwt-secret.txt"   \
    "--authrpc.port"   "{{ node.port_arpc }}"   \
    "--authrpc.vhosts"   '*'   \
    "--config"   "{{ cfg.meta.dir.el }}/{{ node.host }}/config.toml"   \
    "--datadir"  "{{ cfg.meta.dir.el }}/{{ node.host }}"   \
    "--db.engine" "pebble" \
    "--discovery.port"   "{{ node.port_p2p }}"   \
    "--gcmode"   "archive"   \
    "--http.addr"   "0.0.0.0"   \
    "--http.port"   "{{ node.port_rpc }}"   \
    "--http.vhosts"   '*'   \
    "--http"   "--ipcdisable"  \
    "--maxpeers"   "{{ cfg.el.geth_node_count + cfg.el.mev_builder_node_count }}" \
    "--nat"   "none"   \
    "--networkid"   "{{ cfg.el.chain_id }}"  \
    "--nodekeyhex"   "{{ node.key }}"  \
    "--password"   "{{ cfg.meta.dir.el }}/etc/signer-password.txt"   \
    "--port"   "{{ node.port_p2p }}"   \
    "--syncmode"   "full"   \
    "--unlock"   "{{ node.address }}"   \
    "--ws.addr"   "0.0.0.0"   \
    "--ws.origins"   "/ws"   \
    "--ws.port"   "{{ node.port_wsrpc }}" \
    "--ws" \
    "--ipcdisable" \
    "--http" \
    "--http.api" "engine,eth,web3,net,debug,personal,txpool,debug" \
    "--verbosity" "{{ cfg.el.verbosity }}"
