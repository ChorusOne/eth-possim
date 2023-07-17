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
accessed via `docker-compose` utility.

To get fresh privatenet up and running, invoke:

```bash
docker-compose build possim
docker-compose run possim
```

Run with overridden config:

```bash
docker-compose run possim CONFIG=/opt/privatenet/pbs_config.yaml
```

See [configuration.yaml](./eth_possim/resources/configuration.yaml) for the default values.


How it works inside the container
----------------------------------
First, a command `python3 -m eth_possim generate` generates configuration for all
the components.

Then, `tilt up` command starts the blockchain.

And finally, `make` file binds generation and tilt start together.


How to test
-----------
```bash
docker-compose run possim test
```
