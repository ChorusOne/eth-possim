# Init EL nodes
local_resource(
    "el-init",
    cmd="./.data/shell/init-el.sh",
    deps=["cfg-gen-pre"],
)

# Start EL haproxy
local_resource(
    "el-haproxy",
    serve_cmd="./.data/shell/run-haproxy-el.sh",
    deps=["el-init"],
)

cfg = decode_yaml(read_file("./.data/configuration.yaml"))
geth_nodes = []

# Init CL nodes
local_resource(
    "init-cl",
    cmd="./.data/shell/init-cl.sh",
    deps=geth_nodes,
)

# Patch CL config
local_resource(
    "patch-cl",
    cmd="python3 -m eth_possim patch-cl",
    deps=["init-cl"],
)

# Regenerate genesis
local_resource(
    "cl-genesis",
    cmd="./.data/shell/eth2-genesis.sh",
    deps=["init-cl"],
)

# EL boot node
local_resource(
    "el-boot",
    serve_cmd="./.data/shell/run-el-bootnode.sh",
    deps=["cl-genesis"]
)

# CL boot node
local_resource(
    "cl-boot",
    serve_cmd="./.data/shell/run-lh-boot.sh",
    deps=["cl-genesis"]
)



# Deploy EL nodes
for idx, geth_node in enumerate(cfg["el"]["geth_node"]):
    node_name = "el-geth-{}".format(idx)
    local_resource(
        node_name,
        serve_cmd="./.data/shell/run-geth-node-{}.sh".format(idx),
        deps=["cl-boot", "el-boot"],
        allow_parallel=True,
    )
    geth_nodes.append(node_name)

if cfg["pbs"]["enabled"]:

    mev_builder_nodes = []

    # Deploy builder nodes
    for idx, mev_node in enumerate(cfg["el"]["mev_builder_node"]):
        node_name = "el-mev-{}".format(idx)
        local_resource(
            node_name,
            serve_cmd="./.data/shell/run-mev-builder-{}.sh".format(idx),
            deps=["cl-boot", "el-boot"],
            allow_parallel=True,
        )
        mev_builder_nodes.append(node_name)


# Deploy beacon nodes
lh_beacon_nodes = []
for idx in range(cfg["cl"]["lh_node_count"]):
    node_name = "cl-lh-{}".format(idx)
    local_resource(
        node_name,
        serve_cmd="./.data/shell/run-lh-beacon-node-{}.sh".format(idx),
        deps=geth_nodes,
    )
    lh_beacon_nodes.append(node_name)

# Deploy batch deposit contract
local_resource(
    "deploy-deposit-contract",
    cmd="python3 -m eth_possim deploy-batch-deposit-contract",
    deps=lh_beacon_nodes,
    allow_parallel=True,
)

# Deploy validator nodes
for idx in range(cfg["cl"]["lh_node_count"]):
    node_name = "val-lh-{}".format(idx)
    local_resource(
        node_name,
        serve_cmd="./.data/shell/run-lh-validator-node-{}.sh".format(idx),
        deps=lh_beacon_nodes,
    )

# Start CL haproxy
local_resource(
    "cl-haproxy",
    serve_cmd="./.data/shell/run-haproxy-cl.sh",
    deps=lh_beacon_nodes,
)

# Deploy Teku
for idx in range(cfg["cl"]["teku_node_count"]):
    local_resource(
        "cl-teku-{}".format(idx),
        serve_cmd="./.data/shell/run-teku-beacon-node-{}.sh".format(idx),
        deps=lh_beacon_nodes,
    )


if cfg["pbs"]["enabled"]:

    mev_prysm_nodes = []

    # Deploy Prysm
    for idx, node in enumerate(cfg["el"]["mev_builder_node"]):
        node_name = "cl-prysm-mev-{}".format(idx)
        local_resource(
            node_name,
            serve_cmd="./.data/shell/run-mev-prysm-{}.sh".format(idx),
            deps=lh_beacon_nodes + mev_builder_nodes,
        )
        mev_prysm_nodes.append(node_name)


    # Deploy PBS tooling
    local_resource(
        "mev-relay",
        serve_cmd="./.data/shell/run-mev-relay.sh",
        deps=mev_prysm_nodes,
    )
    local_resource(
        "mev-boost",
        serve_cmd="./.data/shell/run-mev-boost.sh",
        deps=["mev-relay"],
    )
