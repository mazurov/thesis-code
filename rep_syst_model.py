#!/usr/bin/env python

import dbtools
import tools
import pdg
import table


def main():
    cfg = tools.load_config("rep_syst_model")

    for ns in range(1, 4):
        cfg_decay = cfg.get("ups%ds" % ns, None)
        if not cfg_decay:
            continue
        bins = tools.axis2bins(cfg_decay["bins"].values())
        valid_bins = {}
        for np in cfg_decay["bins"]:
            valid_bins[int(np)] = tools.axis2bins(cfg_decay["bins"][np])

        tab = table.SqsTable(
            title=cfg["title"].format(ns=ns),
            label=cfg["label"].format(ns=ns),
            ns=ns,
            binning=bins,
            scale=cfg_decay["scale"],
            maxbins=cfg_decay["maxbins"]
        )
        for np in pdg.VALID_UPS_DECAYS[ns]:
            tab.add_row(key=str(np), title=r"$N_{{\chi_b(%dP)}}$" % np)
            if np != pdg.VALID_UPS_DECAYS[ns][-1]:
                tab.space()

        db_ref = tools.get_db(cfg_decay["db_ref"])
        dbs = []
        for db_name in cfg_decay["nchib"]:
            dbs.append(tools.get_db(db_name, "r"))

        for bin in bins:
            for year in ["2011", "2012"]:
                bin_group = tab.get_group(bin, year)
                for np in pdg.VALID_UPS_DECAYS[ns]:
                    if bin in valid_bins[np]:
                        change = dbtools.get_chib_squared_error(
                            db_ref, dbs, np, year, bin
                        )
                        if change is None:
                            value = None
                        else:
                            stat = dbtools.get_chib_yield_err(
                                db_ref, np, year, bin
                            )
                            value = (
                                r"${\pm %.1f \%% \stat}^{+%.1f \%%}_{-%.1f \%%} \syst$" %
                                (stat * 100, change[0] * 100, change[1] * 100)
                            )
                    else:
                        value = None

                    bin_group.add_value(key=str(np), value=value)

        print tab.texify()

if __name__ == '__main__':
    main()
