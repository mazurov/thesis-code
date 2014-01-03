#!/usr/bin/env python

import tools
import table

import AnalysisPython.PyRoUts as pyroot
VE = pyroot.VE


def main():
    cfg = tools.load_config("rep_syst")

    cfg_decay = cfg['ups1s']
    db_ref = tools.get_db(cfg_decay["db"])
    binning = [tuple(x) for x in cfg_decay["binning"]]
    nchib = cfg_decay["nchib"]
    for cfg_table in cfg_decay["tables"]:
        tab = table.SystTable(
            title=cfg_table["title"],
            label=cfg_table["label"],
            binning=binning,
            ns=cfg_decay["ns"],
            nchib=nchib,
            maxbins=cfg_decay["maxbins"],
            scale=cfg_decay['scale']
        )

        for cfg_row in cfg_table['rows']:
            tab.add_row(key=cfg_row["key"], title=cfg_row["title"])
            if cfg_row.get("space", False):
                tab.space()

            db = tools.get_db(cfg_row["db"], "r")
            for bin in binning:
                for data_key in ["2011", "2012"]:
                    db_bin = db[data_key][bin]
                    db_bin_ref = db_ref[data_key][bin]

                    sqs = 7 if data_key == "2011" else 8
                    for np in nchib:
                        np_key = "N%dP" % np
                        value = db_bin.get(np_key, None)
                        value_ref = db_bin_ref.get(np_key, None)
                        if not (value and value_ref):
                            value_change = None
                        else:
                            value_change = (
                                1 - VE(str(value)) / VE(str(value_ref))
                            ) * 100
                            value_change = value_change.value()

                        group = tab.get_group(bin=bin, sqs=sqs, np=np)
                        group.add_value(key=cfg_row["key"], value=value_change, round=1)

        # Fill Table
        print tab.texify( )

if __name__ == '__main__':
    main()
