#!/bin/bash

set -euo pipefail

### Support layer: haproxy (EL) #####################################################

haproxy -V -W -f ./.data/haproxy/el.cfg
