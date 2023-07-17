import os
import logging

import jinja2


logger = logging.getLogger(__name__)


def render(cfg: dict, src: str, dst: str):
    with open(src, "r") as f:
        raw = f.read()
        tpl = jinja2.Environment(undefined=jinja2.StrictUndefined).from_string(raw)
        logging.debug(f"Loaded template from '{os.path.abspath(f.name)}'")

    rendered = tpl.render(cfg=cfg)
    sanitized = _sanitize(rendered)
    with open(dst, "w") as f:
        f.write(sanitized)
        logging.info(f"Generated file '{os.path.abspath(f.name)}'")


def render_with_node(cfg: dict, node: dict, src: str, dst: str):
    with open(src, "r") as f:
        raw = f.read()
        tpl = jinja2.Environment().from_string(raw)
        logging.debug(f"Loaded template from '{os.path.abspath(f.name)}'")

    rendered = tpl.render(cfg=cfg, node=node)
    sanitized = _sanitize(rendered)

    with open(dst, "w") as f:
        f.write(sanitized)
        logging.info(f"Generated file '{os.path.abspath(f.name)}'")


def _sanitize(dc: str) -> str:
    """`sanitize` removes meaningless lines from the rendered file.

    For example, lines that contain only single hash (`#`) symbol, or
    continuous chunks of empty lines, - all the "leftovers" after
    rendering jinja template directives (that are commented out in the
    original template to make linters happy).
    """
    sanitized = ""
    empty = 0
    for line in dc.split("\n"):
        stripped_line = line.strip()

        # Residue after commented out jinja statements => strip
        if stripped_line == "#":
            continue

        # Meaningful line => add
        if stripped_line != "":
            empty = 0
            sanitized += line
            sanitized += "\n"
            continue

        # Empty line => disallow more than 2 consecutive
        empty += 1
        if empty < 2:
            sanitized += "\n"

    return sanitized.strip() + "\n"
