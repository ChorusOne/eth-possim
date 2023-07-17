#!/bin/bash

set -euxo pipefail

# Generate post-merge (Capella-enabled) genesis
genesis_args=(
    capella
    --legacy-config {{ cfg.meta.dir.cl }}/etc/config-prysm.yaml
    --config {{ cfg.meta.dir.cl }}/etc/config-prysm.yaml
    --mnemonics {{ cfg.meta.dir.cl }}/etc/mnemonics.yaml
    --tranches-dir {{ cfg.meta.dir.cl }}/etc/tranches
    --state-output {{ cfg.meta.dir.cl }}/etc/genesis.ssz
    --preset-phase0 minimal
    --preset-altair minimal
    --preset-bellatrix minimal
    --preset-capella minimal
    --eth1-config {{ cfg.meta.dir.el }}/etc/genesis.json
    --eth1-withdrawal-address {{ cfg.el.funder.address }}
    --preset-deneb minimal
)

pretty_args=(
    capella
    BeaconState
    --config {{ cfg.meta.dir.cl }}/etc/config-prysm.yaml
    --preset-phase0 minimal
    --preset-altair minimal
    --preset-bellatrix minimal
    --preset-capella minimal
    --preset-capella {{ cfg.meta.dir.cl }}/etc/config-prysm.yaml
    --preset-deneb minimal
    {{ cfg.meta.dir.cl }}/etc/genesis.ssz
)

genesis_args+=(--eth1-config {{ cfg.meta.dir.el }}/etc/genesis.json)

/usr/local/bin/eth2-testnet-genesis "${genesis_args[@]}"

/usr/local/bin/zcli pretty "${pretty_args[@]}" > "{{ cfg.meta.dir.cl }}/etc/BeaconState.json"

jq -r '.eth1_data.block_hash' "{{ cfg.meta.dir.cl }}/etc/BeaconState.json" > "{{ cfg.meta.dir.cl }}/etc/deposit_contract_block_hash.txt"
