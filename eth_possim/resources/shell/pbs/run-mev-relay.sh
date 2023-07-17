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

export GENESIS_FORK_VERSION="{{ cfg.cl.genesis_fork_version }}"
export FORK_VERSION_CAPELLA="{{ cfg.cl.capella_fork_version }}"
export CHAIN_ID="{{ cfg.el.chain_id }}"
export GENESIS_VALIDATORS_ROOT=$(
    curl -s $cl_api/eth/v1/beacon/genesis | jq -r '.data.genesis_validators_root'
)


mev-freelay \
    --network "possim" \
    --beacons http://127.0.0.1:{{ cfg.cl.lh_node.0.port_api }} \
    --block-sim-url http://127.0.0.1:{{ cfg.el.geth_node.1.port_rpc }} \
    --secret-key {{ cfg.pbs.relay_secret_key }} \
    --db-dir {{ cfg.meta.dir.cl }}/{{ node.host }} \
    --api-addr "127.0.0.1:{{ cfg.cl.mev_relay.port_relay }}" \
    --addr "127.0.0.1:{{ cfg.cl.mev_relay.port_api }}"
