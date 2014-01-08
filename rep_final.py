#!/usr/bin/env python

import dbtools
import tools
import pdg
import table

from functools import partial


def main():
    cfg = tools.load_config("rep_final")
    db_ups = tools.get_db(cfg["db_ups"], "r")
    db_mc = tools.get_db(cfg["db_mc"], "r")

    for ns in range(1, 4):
        cfg_decay = cfg.get("ups%ds" % ns, None)
        if not cfg_decay:
            continue
        bins = tools.axis2bins(cfg_decay["bins"].values())
        valid_bins = {}
        for np in cfg_decay["bins"]:
            valid_bins[int(np)] = tools.axis2bins(cfg_decay["bins"][np])

        tab = table.SqsTable(
            title=cfg["title_final"].format(ns=ns),
            label=cfg["label_final"].format(ns=ns),
            ns=ns,
            binning=bins,
            scale=cfg_decay["scale"],
            maxbins=cfg_decay["maxbins"]
        )
        for np in pdg.VALID_UPS_DECAYS[ns]:
            tab.add_row(key=str(np),
                        title=cfg["row_final_title"].format(ns=ns, np=np))
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
                    syst = None
                    if bin in valid_bins[np]:
                        change = dbtools.get_chib_squared_error(
                            db_ref, dbs, np, year, bin
                        )

                        frac_func = partial(dbtools.get_fraction,
                                            db_chib=db_ref,
                                            db_ups=db_ups,
                                            db_mc=db_mc,
                                            year=year,
                                            bin=bin,
                                            ns=ns,
                                            np=np)
                        frac = frac_func()
                        frac_plus = frac_func(scalecb=(1 + change[0]))
                        frac_minus = frac_func(scalecb=(1 - change[1]))

                        # print "Frac: ", change, frac, frac_plus, frac_minus

                        if not (frac and frac_plus and frac_minus):
                            value = None
                        else:
                            # stat = dbtools.get_chib_yield_err(
                            #     db_ref, np, year, bin
                            # )
                            # value = (
                            #     r"${\pm %.1f \%% \stat}^{+%.1f \%%}_{-%.1f \%%} \syst$" %
                            #     (stat * 100, change[0] * 100, change[1] * 100)
                            # )
                            value = frac * 100
                            syst = (
                                100 * (frac_plus.value() - frac.value()),
                                100 * (frac.value() - frac_minus.value())
                            )
                    else:
                        value = None

                    if syst:
                        bin_group.add_value(
                            key=str(np), value=value, syst=syst, round=1)
                    else:
                        bin_group.add_value(key=str(np), value=value)

        print tab.texify()

if __name__ == '__main__':
    main()
