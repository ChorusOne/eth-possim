#!/bin/bash

set -euxo pipefail

mev-boost \
    "-debug" \
    "-genesis-fork-version" "{{ cfg.cl.genesis_fork_version }}" \
    "-addr" "127.0.0.1:{{ node.port_api }}" \
    "-mainnet" "-relay-check" \
    "-relays" "http://{{ cfg.pbs.relay_public_key }}@127.0.0.1:{{ cfg.cl.mev_relay.port_api }}"
