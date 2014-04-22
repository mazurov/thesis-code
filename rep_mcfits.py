#!/usr/bin/env python

"""Fit report.

Usage:
  ./rep_mcfits.py --ns=<ns>

Options:
  --profile=<profile> Report profile
"""

import tools
import table
import pdg

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
    # cli_args = docopt(__doc__, version='v1.0')

    cfg = tools.load_config("rep_mcfits")
    keys_cfg = cfg["keys"]

    db = tools.get_db(cfg["db"])

    fmt = {}
    for ns in range(1, 4):
        fmt["ns"] = ns
        bins = tools.axis2bins(cfg["binning"]["ups%ds" % ns])
        for np in pdg.VALID_UPS_DECAYS[ns]:
            fmt["np"] = np

            title = cfg["title"].format(**fmt)
            label = cfg["label"].format(**fmt)

            tab = table.SqsTable(
                title=title,
                label=label,
                ns=ns,
                binning=bins,
                scale=cfg["scale"],
                maxbins=cfg["maxbins"]
            )

            for row in cfg["rows"]:
                if row is None:
                    tab.space()
                    continue
                fmt["nb"] = row["nb"]
                chib = cfg["chib"].format(**fmt)
                tab.add_row(
                    key=row["key"],
                    title=get_title(cfg["keys"][row["map"]]).format(chib=chib)
                )

            for bin in bins:
                for data_key in ["mc2011", "mc2012"]:
                    # Add rows
                    group = tab.get_group(bin=bin, sqs=data_key)
                    for nb in range(1, 3):
                        ups_key = "ups%ds" % ns

                        for row in cfg["rows"]:
                            if not row:
                                continue

                            chib_key = "chib%d%dp" % (row['nb'], np)
                            db_fit = db[data_key][ups_key][
                                tuple(bin)][chib_key]

                            value = db_fit.get(row['map'], None)
                            scale = get_scale(cfg["keys"][row['map']])
                            rounds = get_round(cfg["keys"][row['map']])

                            if value and scale:
                                value = VE(str(value)) * scale

                            group.add_value(
                                key=row['key'],
                                value=value,
                                round=rounds
                            )
            print tab.texify()

if __name__ == '__main__':
    main()
