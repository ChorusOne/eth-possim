"""
For newly initialized beacon chain, performs deposit and exit of 2 validators,
via batch contract.
"""
import json
import os
import pytest
import requests
import requests.exceptions
import time
import shlex
import subprocess
import yaml

import eth_possim
from eth_possim.deposit import call_batch_deposit_contract


@pytest.fixture(scope="module")
def tilt_up():
    p = subprocess.Popen("make freshrun", shell=True, stdout=subprocess.PIPE)

    # Wait until config file is provisioned
    while True:
        if not os.path.exists(".data/configuration.yaml"):
            time.sleep(0.5)
        else:
            break

    with open(".data/configuration.yaml") as f:
        cfg = yaml.safe_load(f)
    yield cfg
    p.kill()


def beacon_url(cfg):
    return f"http://127.0.0.1:{cfg['port']['beacon_api']}"


@pytest.mark.run(order=1)
@pytest.mark.timeout(120)
def test_eth_synced(tilt_up):
    base_url = beacon_url(tilt_up)

    # Wait until node is no more syncing
    while True:
        try:
            response = requests.get(f"{base_url}/eth/v1/node/syncing")
        except requests.exceptions.RequestException as e:
            print(f"Failed req: {e}")
            time.sleep(0.5)
        else:
            if response.status_code == 200:
                data = response.json()
                if not data["data"]["el_offline"]:
                    break
                else:
                    print(f"Not synced: {data['data']}")
            else:
                print(f"Response not 200: {response}")
            time.sleep(0.5)

    assert not data["data"]["is_syncing"]


@pytest.mark.run(order=2)
@pytest.mark.timeout(120)
def test_batch_deposit(tilt_up):
    # Wait until batch deposit contract is deployed
    while True:
        with open(".data/configuration.yaml") as f:
            cfg = yaml.safe_load(f)
            if (not cfg) or (cfg and "batch_deposit_contract_address" not in cfg["cl"]):
                time.sleep(0.5)
            else:
                break

    batch_deposit_contract_src = (
        f"{eth_possim.__path__[0]}/resources/solidity/batch-deposit-contract.sol"
    )
    with open(f"{os.path.dirname(__file__)}/deposit_data.json") as f:
        deposit_data = json.load(f)

    receipt = call_batch_deposit_contract(
        batch_deposit_contract_src, *deposit_data["deposit_data"]
    )

    # tx successful
    assert receipt["status"] == 1


def get_validator_by_index(idx, validators):
    for validator in validators["data"]:
        if validator["index"] == str(idx):
            return validator


@pytest.mark.run(order=3)
@pytest.mark.timeout(500)
def test_validator_activated(tilt_up):
    base_url = beacon_url(tilt_up)

    # Wait until validators become pending (total rule 34)
    while True:
        response = requests.get(f"{base_url}/eth/v1/beacon/states/head/validators")
        validators = response.json()
        num_validators = len(validators["data"])
        print(f"Total {num_validators} running, need 34")
        if num_validators == 34:
            val_33 = get_validator_by_index(32, validators)
            val_34 = get_validator_by_index(33, validators)

            assert val_33["status"] in ("pending_initialized", "pending_queued")
            assert val_34["status"] in ("pending_initialized", "pending_queued")

            break
        else:
            time.sleep(5)

    # Wait until validators become active
    while True:
        response = requests.get(f"{base_url}/eth/v1/beacon/states/head/validators")
        validators = response.json()
        val_33 = get_validator_by_index(32, validators)
        val_34 = get_validator_by_index(33, validators)

        val_33_status = val_33["status"]
        val_34_status = val_34["status"]

        print(
            f"Validator_33_status={val_33_status}, Validator_34_status={val_34_status}"
        )

        if val_33_status == val_34_status == "active_ongoing":
            break
        else:
            time.sleep(5)


@pytest.mark.run(order=4)
@pytest.mark.timeout(300)
def test_validator_exited(tilt_up):
    base_url = beacon_url(tilt_up)

    # Wait min_withdrawability_delay + 1 epoch
    print("Waiting for 3 epochs to pass")
    time.sleep(3 * 8 * 3)

    with open(f"{os.path.dirname(__file__)}/deposit_data.json") as f:
        deposit_data = json.load(f)

    # Send exits
    for i, private_key in enumerate(deposit_data["private_keys"]):
        subprocess.check_call(
            shlex.split(
                f"ethdo validator exit --private-key 0x{private_key}  --connection {base_url}"
            )
        )
        print(f"Sent exit to validator #{33 + i}")

    # Wait until validators become exited
    while True:
        response = requests.get(f"{base_url}/eth/v1/beacon/states/head/validators")
        validators = response.json()
        val_33 = get_validator_by_index(32, validators)
        val_34 = get_validator_by_index(33, validators)

        val_33_status = val_33["status"]
        val_34_status = val_34["status"]

        print(
            f"Validator_33_status={val_33_status}, Validator_34_status={val_34_status}"
        )

        if val_33_status == val_34_status == "exited_unslashed":
            break
        else:
            time.sleep(5)
