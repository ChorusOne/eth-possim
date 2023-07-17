#!/bin/bash

set -euxo pipefail

cl_api="http://127.0.0.1:{{ cfg.haproxy.cl.port_api }}"

trap "exit 0" SIGINT
while [[ "$( curl -s -o /dev/null -w "%{http_code}" $cl_api/eth/v1/beacon/genesis )" != "200" ]]; do
    echo "[$( date +"%Y-%m-%dT%H:%M:%S%z" )] ...still waiting for CL genesis"
    sleep 5
done
trap - SIGINT
echo "[$( date +"%Y-%m-%dT%H:%M:%S%z" )] Starting up..."

genesis_validators_root=$(
    curl -s $cl_api/eth/v1/beacon/genesis | jq -r '.data.genesis_validators_root'
)

seconds_per_slot=$(
    curl -s $cl_api/eth/v1/config/spec | jq -r '.data.SECONDS_PER_SLOT'
)

slots_per_epoch=$(
    curl -s $cl_api/eth/v1/config/spec | jq -r '.data.SLOTS_PER_EPOCH'
)

geth-mev-builder \
    --allow-insecure-unlock \
    --authrpc.addr "127.0.0.1" \
    --authrpc.jwtsecret "{{ cfg.meta.dir.el }}/etc/jwt-secret.txt" \
    --authrpc.port "{{ node.port_arpc }}" \
    --authrpc.vhosts "*" \
    --builder \
    --builder.beacon_endpoints "http://127.0.0.1:{{ cfg.cl.mev_prysm_node[node.index].port_api }}" \
    --builder.bellatrix_fork_version "{{ cfg.cl.bellatrix_fork_version }}" \
    --builder.genesis_fork_version "{{ cfg.cl.genesis_fork_version }}" \
    --builder.genesis_validators_root "$genesis_validators_root" \
    --builder.seconds_in_slot "$seconds_per_slot" \
    --builder.slots_in_epoch "$slots_per_epoch" \
    --builder.listen_addr "127.0.0.1:{{ node.port_builder }}" \
    --builder.remote_relay_endpoint "http://127.0.0.1:{{ cfg.cl.mev_relay.port_api }}" \
    --builder.validator_checks \
    --builder.relay_secret_key "{{ cfg.pbs.relay_secret_key }}" \
    --builder.secret_key "{{ node.secret_key }}" \
    --config "{{ cfg.meta.dir.el }}/{{ node.host }}/config.toml" \
    --datadir "{{ cfg.meta.dir.el }}/{{ node.host }}" \
    --discovery.port "{{ node.port_p2p }}" \
    --gcmode "full" \
    --http \
    --http.addr "127.0.0.1" \
    --http.api "db,debug,eth,flashbots,miner,net,personal,txpool,web3" \
    --http.port "{{ node.port_rpc }}" \
    --http.vhosts "*" \
    --ipcdisable \
    --maxpeers "{{ cfg.el.geth_node_count + cfg.el.mev_builder_node_count - 1 }}" \
    --nat "none" \
    --networkid "{{ cfg.el.chain_id }}" \
    --nodekeyhex "{{ node.key }}" \
    --nodiscover \
    --override.shanghai "{{ cfg.el.override_shanghai }}" \
    --password "{{ cfg.meta.dir.el }}/etc/signer-password.txt" \
    --port "{{ node.port_p2p }}" \
    --syncmode "full" \
    --unlock "{{ node.address }}" \
    --ws \
    --ws.addr "127.0.0.1" \
    --ws.origins "/ws" \
    --ws.port "{{ node.port_wsrpc }}" \
    --verbosity "4"
