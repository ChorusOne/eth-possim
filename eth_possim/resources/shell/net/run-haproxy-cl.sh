#!/bin/bash

set -euo pipefail

### Support layer: haproxy (CL) #####################################################

haproxy -V -W -f ./.data/haproxy/cl.cfg
