#!/usr/bin/env python

import dbtools
import tools
import pdg
import table
import math

from functools import partial


def main():
    cfg = tools.load_config("rep_final")
    db_ups = tools.get_db(cfg["db_ups"], "r")
    db_mc = tools.get_db(cfg["db_mc"], "r")
    db_pol = tools.get_db(cfg["db_pol"], "r")["mcall"]

    fmt_syst = r"${}^{+%.1f \%%}_{-%.1f \%%}$"
    fmt_syst_final = r"${}^{+%.1f}_{-%.1f}$"
    fmt_pm_ups = r"$\pm %.3f \%%$"
    fmt_pm_eff = r"$\pm %.2f \%%$"

    tabs_final = []

    for ns in range(1, 4):
        cfg_decay = cfg.get("ups%ds" % ns, None)
        if not cfg_decay:
            continue
        bins = tools.axis2bins(cfg_decay["bins"].values())
        valid_bins = {}
        for np in cfg_decay["bins"]:
            valid_bins[int(np)] = tools.axis2bins(cfg_decay["bins"][np])

        # TODO: add other tables
        tabs = []
        TabFabric = partial(
            table.SqsTable,
            ns=ns,
            binning=bins,
            scale=cfg["scale"],
            maxbins=cfg["maxbins"]
        )

        tab_model = TabFabric(
            title=cfg["title_model"].format(ns=ns),
            label=cfg["label_model"].format(ns=ns),
        )

        tab_ups = TabFabric(
            title=cfg["title_ups"].format(ns=ns),
            label=cfg["label_ups"].format(ns=ns),
        )

        tab_eff = TabFabric(
            title=cfg["title_eff"].format(ns=ns),
            label=cfg["label_eff"].format(ns=ns),
        )

        tab_pol = TabFabric(
            title=cfg["title_pol"].format(ns=ns),
            label=cfg["label_pol"].format(ns=ns),
        )

        tab_final = TabFabric(
            title=cfg["title_final"].format(ns=ns),
            label=cfg["label_final"].format(ns=ns),
        )

        tab_final_pol = TabFabric(
            title=cfg["title_final_pol"].format(ns=ns),
            label=cfg["label_final_pol"].format(ns=ns),
        )

        tab_final.scale = cfg["scale_final"]
        tab_final_pol.scale = cfg["scale_final"]

        tabs.append(tab_model)
        tabs.append(tab_ups)
        tabs.append(tab_eff)
        tabs.append(tab_pol)

        tabs_final.append(tab_final)
        tabs_final.append(tab_final_pol)

        # TODO: add other tables
        for np in pdg.VALID_UPS_DECAYS[ns]:
            for tab in tabs + [tab_final, tab_final_pol]:
                tab.add_row(key=str(np),
                            title=cfg["row_title"].format(ns=ns, np=np))
                if np != pdg.VALID_UPS_DECAYS[ns][-1]:
                    tab.space()

        db_ref = tools.get_db(cfg_decay["db_ref"])
        dbs = []
        for db_name in cfg_decay["nchib"]:
            dbs.append(tools.get_db(db_name, "r"))

        for bin in bins:
            for year in ["2011", "2012"]:
                bin_group_model = tab_model.get_group(bin, year)
                bin_group_ups = tab_ups.get_group(bin, year)
                bin_group_eff = tab_eff.get_group(bin, year)
                bin_group_pol = tab_pol.get_group(bin, year)
                bin_group_final = tab_final.get_group(bin, year)
                bin_group_final_pol = tab_final_pol.get_group(bin, year)

                for np in pdg.VALID_UPS_DECAYS[ns]:
                    if bin in valid_bins[np]:
                        # chib model
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
                        value = frac * 100

                        frac_plus = frac_func(scalecb=(1 + change[0]))
                        frac_minus = frac_func(scalecb=(1 - change[1]))

                        assert frac and frac_plus and frac_minus, "!!!"

                        syst_model = (
                            100 * (frac_plus.value() - frac.value()),
                            100 * (frac.value() - frac_minus.value())
                        )

                        ups_syst = cfg["ups_syst"]
                        frac_plus = frac_func(scaleups=(1 - ups_syst))
                        frac_minus = frac_func(scaleups=(1 + ups_syst))

                        syst_ups = (
                            100 * (frac_plus.value() - frac.value()),
                            100 * (frac.value() - frac_minus.value())
                        )

                        eff_syst = cfg["eff_syst"]
                        frac_plus = frac_func(scaleeff=(1 - eff_syst))
                        frac_minus = frac_func(scaleeff=(1 + eff_syst))

                        syst_eff = (
                            100 * (frac_plus.value() - frac.value()),
                            100 * (frac.value() - frac_minus.value())
                        )

                        change = dbtools.get_polarization_change(
                            db_pol, ns, np, bin
                        )

                        frac_plus = frac_func(scaleeff=(1 - change[1]))
                        frac_minus = frac_func(scaleeff=(1 + change[0]))

                        syst_pol = (
                            100 * (frac_plus.value() - frac.value()),
                            100 * (frac.value() - frac_minus.value())
                        )

                        final_syst = []
                        final_syst_pol = []
                        for i in range(2):
                            final_syst.append(
                                math.sqrt(
                                    syst_model[i] ** 2 +
                                    syst_ups[i] ** 2 +
                                    syst_eff[i] ** 2
                                )
                            )
                            final_syst_pol.append(
                                math.sqrt(
                                    syst_model[i] ** 2 +
                                    syst_ups[i] ** 2 +
                                    syst_eff[i] ** 2 +
                                    syst_pol[i] ** 2
                                )
                            )

                    else:
                        value = None

                    if value:
                        # TODO: collect square roots
                        bin_group_model.add_value(
                            key=str(np),
                            value=fmt_syst % syst_model)
                        bin_group_ups.add_value(
                            key=str(np),
                            value=fmt_pm_ups % syst_ups[0])
                        bin_group_eff.add_value(
                            key=str(np),
                            value=fmt_pm_eff % syst_eff[0])
                        bin_group_eff.add_value(
                            key=str(np),
                            value=fmt_pm_eff % syst_eff[0])
                        bin_group_pol.add_value(
                            key=str(np),
                            value=fmt_syst % syst_pol)

                        final_value = (
                            tools.latex_ve(value) +
                            r"\stat" +
                            fmt_syst_final % tuple(final_syst) +
                            r"\syst \%")
                        final_value_pol = (
                            tools.latex_ve(value) +
                            r"\stat" +
                            fmt_syst_final % tuple(final_syst_pol) +
                            r"\syst \%")

                        bin_group_final.add_value(
                            key=str(np),
                            value=final_value)
                        bin_group_final_pol.add_value(
                            key=str(np),
                            value=final_value_pol)

                    else:
                        bin_group_model.add_value(key=str(np), value=None)
                        bin_group_ups.add_value(key=str(np), value=None)
                        bin_group_eff.add_value(key=str(np), value=None)
                        bin_group_pol.add_value(key=str(np), value=None)
                        bin_group_final.add_value(key=str(np), value=None)
                        bin_group_final_pol.add_value(key=str(np), value=None)

        for tab in tabs:
            print tab.texify()

    print "%% Final tables ============ "
    for tab in tabs_final:
        print tab.texify()

if __name__ == '__main__':
    main()
