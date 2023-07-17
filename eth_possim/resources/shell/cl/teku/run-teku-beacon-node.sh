#!/bin/bash

set -euo pipefail


### Consensus layer: teku beacons ##############################################

export JAVA_OPTS="-Djdk.nio.maxCachedBufferSize=1 -XX:+HeapDumpOnOutOfMemoryError -XX:+UseContainerSupport -XX:HeapDumpPath=/data"

trap "exit 0" SIGINT
while [[ "$( curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:{{ cfg.cl.lh_node[node.index].port_api }}/eth/v2/debug/beacon/states/finalized )" != "200" ]]; do
    echo "[$( date +"%Y-%m-%dT%H:%M:%S%z" )] ...still waiting for genesis (lighthouse should be up then)"
    sleep 5
done
trap - SIGINT
echo "[$( date +"%Y-%m-%dT%H:%M:%S%z" )] Lighthouse is ready.  Starting teku up..."
/opt/teku/bin/teku \
    --p2p-discovery-site-local-addresses-enabled=true  {% if cfg.pbs.enabled -%} --builder-endpoint=http://{{ cfg.pbs.relay_public_key }}@127.0.0.1:{{ cfg.cl.mev_relay.port_relay }} {% endif %}\
    --data-base-path={{ cfg.meta.dir.cl }}/{{ node.host }} \
    --data-storage-mode=archive \
    --ee-endpoint=http://127.0.0.1:{{ cfg.el.geth_node[cfg.cl.lh_node_count + node.index].port_arpc }} \
    --ee-jwt-secret-file={{ cfg.meta.dir.el }}/etc/jwt-secret.txt \
    --initial-state=http://127.0.0.1:{{ cfg.cl.lh_node[node.index].port_api }}/eth/v2/debug/beacon/states/finalized \
    --log-color-enabled=false \
    --log-destination=CONSOLE \
    --logging={{ cfg.cl.debug_level | upper }} \
    --network={{ cfg.meta.dir.cl }}/etc/config.yaml \
    --p2p-advertised-ip=127.0.0.1 \
    --p2p-discovery-bootnodes=$( cat {{ cfg.meta.dir.cl }}/boot/enr/enr.dat ) \
    --p2p-discovery-enabled=true \
    --p2p-peer-lower-bound={{ cfg.cl.lh_node_count + cfg.cl.teku_node_count + cfg.cl.mev_prysm_node_count - 1 }} \
    --p2p-port={{ node.port_p2p }} \
    --p2p-subscribe-all-subnets-enabled=true \
    --rest-api-enabled=true \
    --rest-api-host-allowlist=* \
    --rest-api-port={{ node.port_api }} \
    --validators-graffiti={{ node.host }} \
    --Xlog-wire-cipher-enabled \
    --Xlog-wire-gossip-enabled \
    --Xlog-wire-mux-enabled
