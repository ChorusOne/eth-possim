#
# HETMAN IMAGE
#
# Contains:
# Execution:
#  - Geth + Bootnode util
#
# Consensus:
#  - Lighthouse
#  - Lcli
#  - Teku
#  - Prysm
# Genesis utils:
#  - eth2-testnet-genesis
#  - ethdo
#  - zcli
#  - Flashbots Builder
#  - Flashbots MEV-Boost
#  - Manifold Freelay PBS relay
#

# Base image
ARG DEBIAN_RELEASE="bookworm"

# Lighthouse testnet bakery helper
ARG LCLI_VERSION="4.2.0"

# Ethereum clients
ARG GETH_VERSION="1.12.0"
ARG LIGHTHOUSE_VERSION="4.2.0"
ARG TEKU_VERSION="23.6.0"
ARG MEV_BOOST_VERSION="1.6"

# prysm image
FROM bitnami/minideb:${DEBIAN_RELEASE} AS prysmbuilder

# Bazel build wrapper
ARG BAZELISK_VERSION="1.17.0"
ARG BAZELISK_SHA256="61699e22abb2a26304edfa1376f65ad24191f94a4ffed68a58d42b6fee01e124"

ARG PRYSM_REF="refs/tags/v4.0.6"

ENV BAZELISK_VERSION="${BAZELISK_VERSION}"
ENV PRYSM_REF="${PRYSM_REF}"

RUN install_packages curl ca-certificates git openjdk-17-jdk python3 build-essential libssl-dev libgmp-dev libtinfo5
RUN cd /usr/local/bin/ &&  curl -fsSL  "https://github.com/bazelbuild/bazelisk/releases/download/v${BAZELISK_VERSION}/bazelisk-linux-amd64" -O && mv bazelisk-linux-amd64 bazel
RUN echo "${BAZELISK_SHA256} /usr/local/bin/bazel" | sha256sum -c
RUN chmod +x /usr/local/bin/bazel

WORKDIR /usr/local/src/

RUN git clone https://github.com/prysmaticlabs/prysm.git && cd prysm && git fetch origin "${PRYSM_REF}" && git checkout "${PRYSM_REF}"
    
RUN cd prysm && bazel build //cmd/beacon-chain:beacon-chain --config=minimal
RUN cd prysm && bazel cquery //cmd/beacon-chain:beacon-chain \
    --output starlark \
    --starlark:expr="target.files.to_list()[0].path" > image.txt
RUN mkdir -p /usr/local/prysm/bin
RUN cp "prysm/$(cat prysm/image.txt)" /usr/local/prysm/bin/beacon-chain
RUN find -L /usr/local/prysm

# builder and relay
FROM bitnami/minideb:${DEBIAN_RELEASE} AS mevbuilder
ARG FLASHBOTS_BUILDER_REF="v1.11.5-0.2.1"
ARG MAINIFOLD_FREELAY_REF="support-privatenet"
ENV GO_1_20_SHA256="5a9ebcc65c1cce56e0d2dc616aff4c4cedcfbda8cc6f0288cc08cda3b18dcbf1"

RUN install_packages curl ca-certificates git build-essential
# Install golang
RUN cd /tmp && curl -OL https://golang.org/dl/go1.20.linux-amd64.tar.gz
RUN echo "${GO_1_20_SHA256} /tmp/go1.20.linux-amd64.tar.gz" | sha256sum -c
RUN cd /tmp && tar -C /usr/local -xvf go1.20.linux-amd64.tar.gz

WORKDIR /usr/local/src
RUN git clone https://github.com/ChorusOne/mev-freelay.git relay/ && cd relay && git fetch origin "${MAINIFOLD_FREELAY_REF}" && git checkout "${MAINIFOLD_FREELAY_REF}"
WORKDIR /usr/local/src/relay
ENV PATH="/usr/local/go/bin/:$PATH"
RUN go mod download && mkdir bin/
RUN go build -o ./bin/mev-freelay ./cmd/freelay/main.go && go build -o ./bin/purge ./cmd/purge/main.go && go build -o ./bin/backup ./cmd/backup/main.go && go build -o ./bin/restore ./cmd/restore/main.go && go build -o ./bin/migrate ./cmd/migrate/main.go && go build -o ./bin/compact ./cmd/compact/main.go && go build -o ./bin/import ./cmd/import/main.go
RUN find .


WORKDIR /usr/local/src

RUN git clone https://github.com/flashbots/builder && cd builder && git fetch origin "${FLASHBOTS_BUILDER_REF}" && git checkout "${FLASHBOTS_BUILDER_REF}"
WORKDIR /usr/local/src/builder
RUN PATH="/usr/local/go/bin/:$PATH" go mod download
RUN PATH="/usr/local/go/bin/:$PATH" go run build/ci.go install -static ./cmd/geth


# genesis & zcli tools
FROM bitnami/minideb:${DEBIAN_RELEASE} AS genesisbuilder
# Testnet baking accessories
ARG ZCLI_REF="refs/tags/v0.6.0"
ARG ETH2_TESTNET_GENESIS_REF="refs/tags/v0.8.0"
ENV GO_1_19_SHA256="464b6b66591f6cf055bc5df90a9750bf5fbc9d038722bb84a9d56a2bea974be6"
ENV ZCLI_REF="${ZCLI_REF}"
ENV ETH2_TESTNET_GENESIS_REF="${ETH2_TESTNET_GENESIS_REF}"
WORKDIR /usr/local/src/

RUN install_packages curl ca-certificates git build-essential

# Install golang
RUN cd /tmp && curl -OL https://golang.org/dl/go1.19.linux-amd64.tar.gz
RUN echo "${GO_1_19_SHA256} /tmp/go1.19.linux-amd64.tar.gz" | sha256sum -c
RUN cd /tmp && tar -C /usr/local -xvf go1.19.linux-amd64.tar.gz

# Build zcli
RUN git clone https://github.com/protolambda/zcli.git && cd zcli && git fetch origin "${ZCLI_REF}" && git checkout "${ZCLI_REF}"
RUN cd zcli && PATH="/usr/local/go/bin/:$PATH" go build

# Build genesis tool
RUN git clone https://github.com/protolambda/eth2-testnet-genesis.git && cd eth2-testnet-genesis && git fetch origin "${ETH2_TESTNET_GENESIS_REF}" && git checkout "${ETH2_TESTNET_GENESIS_REF}"
RUN cd eth2-testnet-genesis && PATH="/usr/local/go/bin/:$PATH" go build

# builder and relay
FROM bitnami/minideb:${DEBIAN_RELEASE} AS ethodbuilder
ARG ETHDO_REF="v1.31.0"
ENV GO_1_20_SHA256="5a9ebcc65c1cce56e0d2dc616aff4c4cedcfbda8cc6f0288cc08cda3b18dcbf1"

RUN install_packages curl ca-certificates git build-essential
# Install golang
RUN cd /tmp && curl -OL https://golang.org/dl/go1.20.linux-amd64.tar.gz
RUN echo "${GO_1_20_SHA256} /tmp/go1.20.linux-amd64.tar.gz" | sha256sum -c
RUN cd /tmp && tar -C /usr/local -xvf go1.20.linux-amd64.tar.gz

WORKDIR /usr/local/src/
RUN git clone https://github.com/wealdtech/ethdo.git && cd ethdo && git fetch origin "${ETHDO_REF}" && git checkout "${ETHDO_REF}"
RUN cd ethdo && PATH="/usr/local/go/bin/:$PATH" go mod download
RUN cd ethdo && PATH="/usr/local/go/bin/:$PATH" go build

# geth image
FROM ethereum/client-go:alltools-v${GETH_VERSION} as geth

# lighthouse image
FROM sigp/lighthouse:v${LIGHTHOUSE_VERSION}-amd64-dev as lighthouse

# lcli image
FROM sigp/lcli:v${LCLI_VERSION} as lcli

# teku image
FROM consensys/teku:${TEKU_VERSION}-jdk17 as teku

# mev-boost img
FROM flashbots/mev-boost:${MEV_BOOST_VERSION} as mevboost

# install fresh haproxy (debian stock version is buggy)
FROM bitnami/minideb:${DEBIAN_RELEASE} as haproxy
ENV HAPROXY_SHA256="82d2e64f5537506e49a8ebbde87d6317470fdec0cf288a02b726b8f05788c64d"

RUN install_packages curl ca-certificates liblua5.3-0 libopentracing-c-wrapper0
RUN cd /tmp && \
  curl -L https://ppa.launchpadcontent.net/vbernat/haproxy-2.8/ubuntu/pool/main/h/haproxy/haproxy_2.8.1-1ppa1~jammy_amd64.deb -o /tmp/haproxy.deb \
  && echo "${HAPROXY_SHA256} /tmp/haproxy.deb" | sha256sum -c \
  && dpkg -i /tmp/haproxy.deb

# ============= MAIN IMAGE ================
FROM bitnami/minideb:${DEBIAN_RELEASE} AS builder

RUN install_packages \
  python3 \
  python3-pip \
  python3-venv \
  openjdk-17-jdk-headless \
  unzip \
  curl \
  sudo \
  iblua5.3-0 \
  libopentracing-c-wrapper0 \
  make \
  net-tools \
  dnsutils \
  procps \
  psmisc \
  jq

# Install Tilt
RUN curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash

COPY --from=prysmbuilder /usr/local/prysm/bin/beacon-chain /usr/local/bin/prysm-beacon-chain


# Copy genesis & zcli tools from builder
COPY --from=genesisbuilder /usr/local/src/eth2-testnet-genesis/eth2-testnet-genesis /usr/local/bin/eth2-testnet-genesis
COPY --from=genesisbuilder /usr/local/src/zcli/zcli /usr/local/bin/zcli

# Copy client executables into the container
COPY --from=geth /usr/local/bin/geth /usr/bin/geth
COPY --from=geth /usr/local/bin/bootnode /usr/bin/bootnode
COPY --from=lighthouse /usr/local/bin/lighthouse /usr/local/bin/lighthouse
COPY --from=lcli /usr/local/bin/lcli /usr/local/bin/lcli
COPY --from=teku /opt/teku /opt/teku
COPY --from=mevbuilder /usr/local/src/builder/build/bin/geth /usr/local/bin/geth-mev-builder
COPY --from=mevbuilder /usr/local/src/relay/bin/mev-freelay /usr/local/bin/mev-freelay
COPY --from=mevboost /app/mev-boost /usr/local/bin/mev-boost
COPY --from=ethodbuilder /usr/local/src/ethdo/ethdo /usr/local/bin/ethdo

# Copy haproxy
COPY --from=haproxy /usr/sbin/haproxy /usr/local/bin/haproxy

WORKDIR /opt/privatenet
RUN python3 -m venv venv
COPY requirements.txt /opt/privatenet/requirements.txt
RUN venv/bin/python3 -m pip install -r requirements.txt
COPY setup.py MANIFEST.in README.md LICENSE Tiltfile Makefile /opt/privatenet/
COPY eth_possim /opt/privatenet/eth_possim
RUN venv/bin/python3 setup.py install
ENV PATH="/opt/privatenet/venv/bin:$PATH"
ENV PYTHONPATH="/opt/privatenet/:${PYTHONPATH}"
ENTRYPOINT [ "make" ]
