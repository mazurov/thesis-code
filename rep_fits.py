#!/usr/bin/env python

"""Fit report.

Usage:
  ./rep_fit.py --profile=<profile>

Options:
  --profile=<profile> Report profile
"""

import tools
import table
from docopt import docopt

from AnalysisPython.PyRoUts import VE


def get_title(row_cfg):
    if isinstance(row_cfg, str):
        return row_cfg
    return row_cfg["title"]


def get_scale(row_cfg):
    if isinstance(row_cfg, str):
        return None
    return row_cfg.get("scale", None)


def get_round(row_cfg):
    if isinstance(row_cfg, str):
        return None
    return row_cfg.get("round", None)


def main():
    cli_args = docopt(__doc__, version='v1.0')

    cfg = tools.load_config("rep_fits")
    keys_cfg = cfg["keys"]

    fit_key = cli_args["--profile"]

    cfg_tab = cfg[fit_key]
    db = tools.get_db(cfg_tab["db"])
    tab = table.SqsTable(
        title=cfg_tab["title"],
        label=cfg_tab["label"],
        ns=cfg_tab["ns"],
        binning=cfg_tab["binning"],
        scale=cfg_tab["scale"],
        maxbins=cfg_tab["maxbins"])
    scales = {}
    rounds = {}
    for row_key in cfg_tab['rows']:
        if not row_key:
            tab.space()
            continue
        scales[row_key] = get_scale(keys_cfg[row_key])
        rounds[row_key] = get_round(keys_cfg[row_key])
        tab.add_row(key=row_key, title=get_title(keys_cfg[row_key]))

    for data_key in ["2011", "2012"]:
        for bin in cfg_tab["binning"]:
            db_bin = db[data_key][tuple(bin)]
            for row_key in cfg_tab['rows']:
                if not row_key:
                    continue

                value = db_bin.get(row_key, None)
                if value and scales[row_key]:
                    value = VE(str(value)) * scales[row_key]
                group = tab.get_group(bin=bin, sqs=data_key)
                group.add_value(key=row_key, value=value,
                                round=rounds[row_key])

    print tab.texify()


if __name__ == '__main__':
    main()
