import os
import re
import logging


def ensure_dir_exists(dir: str):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        logging.info(f"Created directory '{os.path.abspath(dir)}'")


def ensure_key_exists(dict: dict, key: str):
    if key not in dict:
        dict[key] = {}


def hexes_as_strings(input: str) -> str:
    output = ""
    for line in input.splitlines():
        line = re.sub(r"(\w+: *)(0x(\d|\w)+)", r'\1"\2"', line)
        output += line
        output += "\n"
    return output


def hexes_as_hexes(input: str) -> str:
    output = ""
    for line in input.splitlines():
        line = re.sub(r"(\w+: *)'(0x(\d|\w)+)'", r"\1\2", line)
        line = re.sub(r'(\w+: *)"(0x(\d|\w)+)"', r"\1\2", line)
        output += line
        output += "\n"
    return output


# https://stackoverflow.com/a/30463972
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(path, mode)
