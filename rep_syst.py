#!/usr/bin/env python

""" Systematic report.

Usage:
  ./rep_syst.py
"""


import tools
import table
import pdg

import AnalysisPython.PyRoUts as pyroot
VE = pyroot.VE

from docopt import docopt


def main():
    cli_args = docopt(__doc__, version="1.0")
    cfg = tools.load_config("rep_syst")

    for ns in range(2, 3):
        cfg_decay = cfg["ups%ds" % ns]
        db_ref = tools.get_db(cfg_decay["db"])

        bins = tools.axis2bins(cfg_decay["axis"].values())
        valid_bins = {}
        for np in cfg_decay["axis"]:
            valid_bins[int(np)] = tools.axis2bins(cfg_decay["axis"][np])

        # Check presence
        # ====================================================================
        check_dbs = []
        for cfg_row in cfg_decay["tables"]:
            for row in cfg_row["rows"]:
                check_dbs.append(row["db"])

        check_bins = set()
        for np in cfg_decay["axis"]:
            check_bins.update(tools.axis2bins(cfg_decay["axis"][np]))

        ok = True
        for data_key in ["2011", "2012"]:
            for dbpath in check_dbs:
                db = tools.get_db(dbpath, "r")
                for bin in sorted(check_bins):
                    db_year = db[data_key]
                    if bin not in db_year:
                        ok = False
                        print("DB %s: No bin %s for Y(%dS) decays in %s" % (
                            dbpath, str(bin), ns, data_key)
                        )
                db.close()
        if not ok:
            continue
        # ====================================================================

        for cfg_table in cfg_decay["tables"]:
            scale = (cfg_table['scale'] if "scale" in cfg_table
                     else cfg_decay['scale'])
            tab = table.SystTable(
                title=cfg_table["title"],
                label=cfg_table["label"],
                binning=bins,
                ns=ns,
                nchib=pdg.VALID_UPS_DECAYS[ns],
                maxbins=cfg_decay["maxbins"],
                scale=scale
            )

            for cfg_row in cfg_table['rows']:
                tab.add_row(key=cfg_row["key"], title=cfg_row["title"])
                if cfg_row.get("space", False):
                    tab.space()

                db = tools.get_db(cfg_row["db"], "r")
                for bin in bins:
                    for data_key in ["2011", "2012"]:
                        db_bin = db[data_key][bin]
                        db_bin_ref = db_ref[data_key][bin]

                        sqs = 7 if data_key == "2011" else 8
                        for np in pdg.VALID_UPS_DECAYS[ns]:
                            np_key = "N%dP" % np

                            value = db_bin.get(np_key, None)
                            value_ref = db_bin_ref.get(np_key, None)

                            if not (bin in valid_bins[np] and value and value_ref):
                                value_change = None
                            else:
                                value_change = (
                                    1 - VE(str(value)) / VE(str(value_ref))
                                ) * 100
                                value_change = value_change.value()

                            group = tab.get_group(bin=bin, sqs=sqs, np=np)

                            group.add_value(
                                key=cfg_row["key"], value=value_change, round=1)

            # Fill Table
            print(tab.texify())

if __name__ == '__main__':
    main()
