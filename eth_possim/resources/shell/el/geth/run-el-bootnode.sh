#!/bin/bash

set -euo pipefail

### Execution layer: bootnode ######################################################

bootnode \
    -nodekeyhex "{{ cfg.el.bootnode_key }}" \
    -addr ":{{ cfg.el.bootnode.port_rpc }}"
