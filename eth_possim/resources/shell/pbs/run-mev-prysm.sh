#!/bin/bash

set -exuo pipefail


prysm-beacon-chain \
      "--accept-terms-of-use" \
      "--bootstrap-node" "{{ cfg.meta.dir.cl }}/etc/boot_enr.yaml" \
      "--chain-config-file" "{{ cfg.meta.dir.cl }}/etc/config-prysm.yaml" \
      "--chain-id" "{{ cfg.cl.deposit_chain_id }}" \
      "--datadir" "{{ cfg.meta.dir.cl }}/{{ node.host }}" \
      "--deposit-contract" "{{ cfg.cl.deposit_contract_address }}" \
      "--disable-monitoring" \
      "--execution-endpoint" "http://127.0.0.1:{{ cfg.el.mev_builder_node[node.index].port_arpc }}" \
      "--genesis-beacon-api-url" "http://127.0.0.1:{{ cfg.cl.lh_node[node.index].port_api }}/eth/v2/debug/beacon/states/finalized" \
      "--grpc-gateway-host" "0.0.0.0" \
      "--grpc-gateway-port" "{{ node.port_api }}" \
      "--jwt-secret" "{{ cfg.meta.dir.el }}/etc/jwt-secret.txt" \
      "--p2p-max-peers" "{{ cfg.cl.lh_node_count + cfg.cl.teku_node_count + cfg.cl.mev_prysm_node_count - 1 }}" \
      "--p2p-tcp-port" "{{ node.port_p2p }}" \
      "--p2p-udp-port" "{{ node.port_p2p }}" \
      "--p2p-host-ip" "127.0.0.1" \
      "--rpc-host" "127.0.0.1" \
      "--rpc-port" "{{ node.port_rpc }}" \
      "--subscribe-all-subnets" \
      "--suggested-fee-recipient" "{{ cfg.el.funder.address }}"
