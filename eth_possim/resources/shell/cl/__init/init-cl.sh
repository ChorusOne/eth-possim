#!/bin/bash

set -eo pipefail

THIS_SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd)"

function run {
    echo "$" "$@" >&2
    eval $( printf '%q ' "$@" )
}


# Render mnemonics

echo '
- mnemonic: "{{ cfg.cl.genesis_mnemonic }}"
  count: {{ cfg.cl.min_genesis_active_validator_count }}
' > $THIS_SCRIPT_DIR/../cl/etc/mnemonics.yaml


# Generate Lighthouse testnet. The Genesis will be regenerated later.
run lcli new-testnet \
          --deposit-contract-address {{ cfg.cl.deposit_contract_address }} \
          --altair-fork-epoch {{ cfg.cl.altair_fork_epoch }} \
          --bellatrix-fork-epoch {{ cfg.cl.bellatrix_fork_epoch }} \
          --capella-fork-epoch {{ cfg.cl.capella_fork_epoch }} \
          --eth1-follow-distance 1 \
          --eth1-id {{ cfg.cl.deposit_chain_id }} \
          --force \
          --eth1-block-hash {{ cfg.cl.eth1_block_hash }} \
          --genesis-delay {{ cfg.cl.genesis_delay }} \
          --genesis-fork-version {{ cfg.cl.genesis_fork_version }} \
          --validator-count  {{ cfg.cl.min_genesis_active_validator_count }} \
          --min-genesis-active-validator-count {{ cfg.cl.min_genesis_active_validator_count }} \
          --min-genesis-time {{ cfg.cl.min_genesis_time }} \
          --proposer-score-boost {{ cfg.cl.proposer_score_boost }} \
          --seconds-per-eth1-block {{ cfg.cl.seconds_per_eth1_block }} \
          --seconds-per-slot {{ cfg.cl.seconds_per_slot }} \
          --spec {{ cfg.cl.preset_base }} \
          --testnet-dir {{ cfg.meta.dir.cl }}/etc \
          --derived-genesis-state \
          --mnemonic-phrase "{{ cfg.cl.genesis_mnemonic }}"

# Generate mnemonics validators for Lighthouse
mkdir -p {{ cfg.meta.dir.cl }}
run lcli mnemonic-validators \
     --base-dir {{ cfg.meta.dir.cl }} \
     --testnet-dir {{ cfg.meta.dir.cl }}/etc \
     --count {{ cfg.cl.min_genesis_active_validator_count }} \
     --node-count {{ cfg.cl.lh_node_count }} \
     --spec {{ cfg.cl.preset_base }} \
     --mnemonic-phrase '{{ cfg.cl.genesis_mnemonic }}'

# Remove dummy genesis
rm "{{ cfg.meta.dir.cl }}/etc/genesis.ssz"


# Generate bootnode ENR (for localhost)
run lcli generate-bootnode-enr \
    --genesis-fork-version {{ cfg.cl.bellatrix_fork_version }} \
    --ip 127.0.0.1 \
    --output-dir {{ cfg.meta.dir.cl }}/boot/enr \
    --tcp-port {{ cfg.cl.lh_boot.port }} \
    --udp-port {{ cfg.cl.lh_boot.port }} \
     --testnet-dir {{ cfg.meta.dir.cl }}/etc

enr=$( cat {{ cfg.meta.dir.cl }}/boot/enr/enr.dat )
echo "- $enr" > {{ cfg.meta.dir.cl }}/etc/boot_enr.yaml
