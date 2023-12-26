eth-possim
==========

Run full-featured Ethereum PoS simulator (private net) locally or in CI/CD,
with PBS (MEV) emulation support.

This project exists to provide convenient and reliable testing
environment with predictable performance for Ethereum API users,
such as developers of PoS blockchain automation.


Execution client support:

- [x] Geth
- [ ] Nethermind
- [ ] Besu
- [ ] Erigon

Consensus client support:

- [x] Lighthouse
- [x] Teku
- [ ] Prysm
- [ ] Nimbus
- [ ] Lodestar


Validator client support:

- [x] Lighthouse
- [ ] Teku
- [ ] Prysm
- [ ] Nimbus
- [ ] Lodestar


The aim is to eventually support all Ethereum clients featured at
[official documentation](https://ethereum.org/en/developers/docs/nodes-and-clients/).


How to use
----------

The primary interface for users is the container one,
accessed via `docker compose` utility (docker compose v2, do not confuse with
v2 of the docker-compose spec, which is obsolete).

First, chose how you want to run the project and save your configuration in the
`.env` file:

* if you're using the opus devpod (internal chorus one project) run:
```bash
echo "COMPOSE_FILE=compose-devpod.yaml" > .env
echo "COMPOSE_PROJECT_NAME=${C1_DOCKER_NAMESPACE}-possim" >> .env
echo "POSSIM_DOCKER_NETWORK=${C1_DOCKER_NETWORK}" >> .env
echo "POSSIM_BINDMOUNT_PATH=$(host-path-outside-of-docker.sh .)" >> .env
echo "POSSIM_HOSTNAME=${C1_DOCKER_NAMESPACE}-possim.devel" >> .env
```
* otherwise for linux host networking configuration run: 
```bash
echo "COMPOSE_FILE=compose-host.yaml" > .env
echo "POSSIM_HOSTNAME=127.0.0.1" >> .env
```

Once you've set up your env you can get the privatenet up and running using:

```bash
docker compose build possim
docker compose run --use-aliases --rm possim
```

Once running, you can connect using:

```bash
source .env
curl -v http://$POSSIM_HOSTNAME:15050
```

To run with overridden config:

```bash
docker compose run --use-aliases --rm possim CONFIG=/opt/privatenet/pbs_config.yaml
```

See [configuration.yaml](./eth_possim/resources/configuration.yaml) for the default values.

How to test
-----------
```bash
docker compose run --rm possim test
```

How it works inside the container
----------------------------------
First, a command `python3 -m eth_possim generate` generates configuration for all
the components.

Then, `tilt up` command starts the blockchain.

And finally, `make` file binds generation and tilt start together.