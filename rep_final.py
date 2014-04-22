#!/usr/bin/env python

import dbtools
import tools
import pdg
import table
import tmpl
import math


from functools import partial

import ROOT
# import AnalysisPython.PyRoUts as pyroot

from graph import Graph
from IPython import embed as shell  # noqa


def print_summary(max_syst_ns, decay_tmpl):
    result = ""
    fmt = "${}^{+%.1f}_{-%.1f}$"
    for ns in range(3, 4):
        for np in pdg.VALID_UPS_DECAYS[ns]:
            max_model, min_model, max_pol, min_pol = [
                x * 100 for x in max_syst_ns[ns][np]
            ]
            result += "\\rule{0pt}{4ex}"
            result += decay_tmpl.format(ns=ns, np=np) + " & "
            result += fmt % (max_model, min_model) + " & "
            result += fmt % (max_pol, min_pol)
            result += "\\\\\n"
    context = {"summary": result}
    tex = tmpl.tex_renderer()
    print(tex.render_name("syst_summary", context))


def save_values(cfg, db, values):
    for year in ["2011", "2012"]:
        result = {}
        for ns in range(3, 4):
            ups_key = "ups%ds" % ns
            result[ups_key] = {}
            for np in pdg.VALID_UPS_DECAYS[ns]:
                chib_key = "chib%dp" % np
                result[ups_key][chib_key] = {}
                bins = tools.axis2bins(cfg[ups_key]["bins"][str(np)])
                for bin in bins:
                    ve, plus, neg = values[ns][bin][year][np]
                    plus_sq = math.sqrt(ve.error() ** 2 + plus ** 2)
                    neg_sq = math.sqrt(ve.error() ** 2 + neg ** 2)

                    result[ups_key][chib_key][bin] = (
                        ve.value(), plus_sq, neg_sq,
                        ve.error(), plus, neg)
        db[year] = result

    print(db)
    db.sync()


def draw_graphs(cfg, values):
    for ns in range(3, 4):
        ups_key = "ups%ds" % ns
        for np in pdg.VALID_UPS_DECAYS[ns]:
            output = "results/%s_%d" % (ups_key, np)
            bins = tools.axis2bins(cfg[ups_key]["bins"][str(np)])
            graphs = []
            for year in ["2011", "2012"]:
                gr_stat = ROOT.TGraphAsymmErrors(len(bins))
                gr_syst = ROOT.TGraphAsymmErrors(len(bins))

                gr_stat.SetMarkerColor(Graph.colors[year][0])
                gr_stat.SetLineColor(Graph.colors[year][0])
                gr_stat.SetMarkerStyle(Graph.colors[year][1])

                gr_syst.SetMarkerColor(Graph.colors[year][0])
                gr_syst.SetLineColor(Graph.colors[year][0])
                gr_syst.SetMarkerStyle(Graph.colors[year][1])

                cfg_graph = cfg[ups_key]["graphs"][str(np)]
                gr_stat.SetMinimum(cfg_graph.get("ymin", 0))
                gr_stat.SetMaximum(cfg_graph.get("ymax", 100))

                for i, bin in enumerate(bins):
                    xc = (bin[0] + float(bin[1] - bin[0]) / 2.0 +
                          (-0.3 if year == "2011" else + 0.3))
                    xe_low = xc - bin[0]
                    xe_high = bin[1] - xc

                    ve, plus, neg = values[ns][bin][year][np]
                    gr_stat.SetPoint(i, xc, ve.value())
                    gr_stat.SetPointError(i, xe_low, xe_high, ve.error(),
                                          ve.error())

                    gr_syst.SetPoint(i, xc, ve.value())
                    gr_syst.SetPointError(i, 0, 0, neg, plus)
                    # gr_stat.SetPoint(i, ve.value(), ve.error())
                opts = "AP"
                if year == "2012":
                    opts = "P"
                gr_stat.Draw(opts)
                gr_stat.GetXaxis().SetLimits(5, 40)
                gr_syst.Draw("P")

                graphs += [gr_stat, gr_syst]

            tools.save_figure(output)

            # Separately save plot with old result
            if ns == 1 and np == 1:
                year = "2010"
                old_values = cfg[ups_key]["2010"]
                gr_old = ROOT.TGraphErrors(len(old_values))
                for i, bin_value in enumerate(old_values):
                    bin, value = bin_value
                    xc = bin[0] + float(bin[1] - bin[0]) / 2.0
                    xe = bin[1] - xc
                    gr_old.SetPoint(i, xc, value[0])
                    gr_old.SetPointError(i, xe, value[1])
                    gr_old.SetMarkerColor(Graph.colors[year][0])
                    gr_old.SetLineColor(Graph.colors[year][0])
                    gr_old.SetMarkerStyle(Graph.colors[year][1])

                gr_old.Draw("P")
                tools.save_figure(output + "_old")


def main():
    cfg = tools.load_config("rep_final")
    db_ups = tools.get_db(cfg["db_ups"], "r")
    db_mc = tools.get_db(cfg["db_mc"], "r")
    db_pol = tools.get_db(cfg["db_pol"], "r")["mcall"]

    db_out = tools.get_db(cfg["db_out"])

    fmt_syst = r"${}^{+%.2f \%%}_{-%.2f \%%}$"
    fmt_syst_final = (r"%s\stat${}^{+%.1f}_{-%.1f}\syst"
                      "^{+%.1f}_{-%.1f}\systpol \%%$")
    fmt_pm_ups = r"$\pm %.3f \%%$"
    fmt_pm_eff = r"$\pm %.2f \%%$"

    tabs_final = []

    graph_values = {}
    max_syst_ns = {}
    for ns in range(3, 4):
        cfg_decay = cfg.get("ups%ds" % ns, None)
        if not cfg_decay:
            continue
        bins = tools.axis2bins(cfg_decay["bins"].values())
        valid_bins = {}
        for np in cfg_decay["bins"]:
            valid_bins[int(np)] = tools.axis2bins(cfg_decay["bins"][np])

        graph_values[ns] = {}
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

        tab_final.maxbins = cfg["maxbins_final"]
        tab_final.scale = cfg["scale_final"]

        tabs.append(tab_model)
        tabs.append(tab_ups)
        tabs.append(tab_eff)
        tabs.append(tab_pol)

        tabs_final.append(tab_final)

        # TODO: add other tables
        for np in pdg.VALID_UPS_DECAYS[ns]:
            for tab in tabs + [tab_final]:
                tab.add_row(key=str(np),
                            title=cfg["row_title"].format(ns=ns, np=np))
                if np != pdg.VALID_UPS_DECAYS[ns][-1]:
                    tab.space()

        db_ref = tools.get_db(cfg_decay["db_ref"])
        dbs = []

        for db_name in cfg_decay["nchib"]:
            db = tools.get_db(db_name, "r")
            # print db_name
            # print sorted(db['2011'].keys())
            # print sorted(db['2012'].keys())
            dbs.append(db)

        max_syst_np = {}

        for bin in bins:
            graph_values[ns][bin] = {}
            for year in ["2011", "2012"]:
                graph_values[ns][bin][year] = {}

                bin_group_model = tab_model.get_group(bin, year)
                bin_group_ups = tab_ups.get_group(bin, year)
                bin_group_eff = tab_eff.get_group(bin, year)
                bin_group_pol = tab_pol.get_group(bin, year)
                bin_group_final = tab_final.get_group(bin, year)

                for np in pdg.VALID_UPS_DECAYS[ns]:
                    graph_values[ns][bin][year][np] = {}

                    if bin in valid_bins[np]:
                        max_model, min_model, max_pol, min_pol = (
                            max_syst_np.get(np, (0, 0, 0, 0))
                        )
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

                        # frac_plus = frac_func(scalecb=(1 + change[0]))
                        # frac_minus = frac_func(scalecb=(1 - change[1]))

                        # assert frac and frac_plus and frac_minus, "!!!"

                        # syst_model = (
                        #     100 * (frac_plus.value() - frac.value()),
                        #     100 * (frac.value() - frac_minus.value())
                        # )

                        syst_model = (
                            change[0],
                            change[1]
                        )

                        # change_model = (
                        #     100 * (frac_plus / frac - 1).value(),
                        #     100 * (1 - frac_minus / frac).value(),
                        # )

                        max_model, min_model = (
                            max(max_model, change[0]),
                            max(min_model, change[1])
                        )

                        ups_syst = cfg["ups_syst"]
                        # frac_plus = frac_func(scaleups=(1 - ups_syst))
                        # frac_minus = frac_func(scaleups=(1 + ups_syst))

                        syst_ups = (
                            ups_syst,
                            ups_syst
                        )

                        # change_ups = (
                        #     100 * (frac_plus / frac - 1).value(),
                        #     100 * (1 - frac_minus / frac).value(),
                        # )

                        eff_syst = cfg["eff_syst"]
                        # frac_plus = frac_func(scaleeff=(1 - eff_syst))
                        # frac_minus = frac_func(scaleeff=(1 + eff_syst))

                        syst_eff = (
                            eff_syst,
                            eff_syst
                        )

                        # change_eff = (
                        #     100 * (frac_plus / frac - 1).value(),
                        #     100 * (1 - frac_minus / frac).value(),
                        # )

                        change = dbtools.get_polarization_change(
                            db_pol, ns, np, bin
                        )

                        # frac_plus = frac_func(scaleeff=(1 - change[1]))
                        # frac_minus = frac_func(scaleeff=(1 + change[0]))

                        syst_pol = (
                            change[1],
                            change[0]
                        )

                        # change_pol = (
                        #     100 * (frac_plus / frac - 1).value(),
                        #     100 * (1 - frac_minus / frac).value(),
                        # )

                        max_pol, min_pol = (
                            max(max_pol, change[1]),
                            max(min_pol, change[0])
                        )

                        max_syst_np[np] = (
                            max_model, min_model, max_pol, min_pol)

                        final_syst = []
                        for i in range(2):
                            final_syst.append(
                                math.sqrt(
                                    syst_model[i] ** 2 +
                                    syst_ups[i] ** 2 +
                                    syst_eff[i] ** 2
                                )
                            )

                        final_graph = []
                        for i in range(2):
                            final_graph.append(
                                math.sqrt(
                                    (value.value() * final_syst[i]) ** 2 +
                                    (value.value() * syst_pol[i]) ** 2 +
                                    value.error() ** 2
                                )
                            )

                        graph_values[ns][bin][year][np] = (
                            value, final_graph[0], final_graph[1]
                        )
                        # if ns == 3:
                        #     shell()
                        #     exit(1)

                    else:
                        value = None

                    if value:
                        # TODO: collect square roots
                        # bin_group_model.add_value(
                        #     key=str(np),
                        #     value=fmt_syst % change_model)
                        # bin_group_ups.add_value(
                        #     key=str(np),
                        #     value=fmt_pm_ups % change_ups[0])
                        # bin_group_eff.add_value(
                        #     key=str(np),
                        #     value=fmt_pm_eff % change_eff[0])
                        # bin_group_pol.add_value(
                        #     key=str(np),
                        #     value=fmt_syst % syst_pol)

                        final_value = (fmt_syst_final %
                                       (tools.latex_ve(value),
                                        value * final_syst[0],
                                        value * final_syst[1],
                                        value * syst_pol[0],
                                        value * syst_pol[1]
                                        ))

                        bin_group_final.add_value(
                            key=str(np),
                            value=final_value)

                    else:
                        bin_group_model.add_value(key=str(np), value=None)
                        bin_group_ups.add_value(key=str(np), value=None)
                        bin_group_eff.add_value(key=str(np), value=None)
                        bin_group_pol.add_value(key=str(np), value=None)
                        bin_group_final.add_value(key=str(np), value=None)

        max_syst_ns[ns] = max_syst_np
        # for tab in tabs:
        #     if tab not in [tab_ups, tab_eff, tab_]
        #     print tab.texify()
    print "%% Final tables ============ "
    for tab in tabs_final:
        print tab.texify()

    print_summary(max_syst_ns, cfg["decay_tmpl"])

    draw_graphs(cfg, graph_values)
    save_values(cfg, db_out, graph_values)

if __name__ == '__main__':
    main()
