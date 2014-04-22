#!/usr/bin/env python

from IPython import embed as shell  # noqa

import tools
import mctools
import pdg
import graph
import table

from collections import defaultdict


def process(db_name, data_key, ns, np):
    # mc = mctools.MC(db_name, data_key, ns, np)

    # for nb in range(1,3):
    pass


def create_table(label, title, scale, cfg_rows, ns, np, binning, maxbins):
    tab = table.PtTable(
        title=title,
        label=label,
        ns=ns,
        binning=binning,
        scale=scale,
        maxbins=maxbins
    )

    for nb in range(1, 3):
        for i in range(3):
            key = cfg_rows[i]["key"].format(nb=nb, np=np, ns=ns)
            title = cfg_rows[i]["title"].format(nb=nb, np=np, ns=ns)
            tab.add_row(key=key, title=title)
        tab.space()
    tab.line()
    title = cfg_rows[3]["title"].format(nb=nb, np=np, ns=ns)
    tab.add_row(key=cfg_rows[3]["key"], title=title)
    return tab


def main():
    cfg_rep = tools.load_config("rep_mceff")

    db = tools.get_db(cfg_rep["db"], "r")

    for ns in range(1, 4):
        graph_values = {
            "mc2011": defaultdict(list),
            "mc2012": defaultdict(list),
        }
        for np in pdg.VALID_UPS_DECAYS[ns]:
            title = cfg_rep["title"].format(
                ns=ns,
                np=np
            )
            label = cfg_rep["label"].format(
                ns=ns,
                np=np
            )
            ups_key = "ups%ds" % ns
            axis = cfg_rep["axis"]["ups%ds" % ns]

            bins = tools.axis2bins(axis)
            maxbins = cfg_rep["maxbins"]

            tab = create_table(label=label, title=title,
                               scale=cfg_rep["scale"],
                               cfg_rows=cfg_rep["rows"],
                               ns=ns, np=np, binning=bins, maxbins=maxbins)

            for bin in bins:
                for data_key in ["mc2011", "mc2012"]:
                    mc = mctools.MC(db=db[data_key][ups_key], ns=ns, np=np)
                    bin_group = tab.get_bin(bin)
                    data_group = bin_group.add_subgroup(
                        key=data_key,
                        title=cfg_rep["data_titles"][data_key]
                    )
                    for nb in range(1, 3):
                        nchib, nups, eff = (
                            mc.nchib(bin, nb),
                            mc.nups(bin, nb),
                            mc.eff(bin, nb))

                        assert(nchib.value() != 0)
                        assert(nups.value() != 0)
                        assert(eff.value() != 0)

                        data_group.add_value("n%d" % nb, nchib)
                        data_group.add_value("nups%d" % nb, nups)
                        data_group.add_value("eff%d" % nb,
                                             eff * 100,
                                             is_bold=True)
                    eff = mc.eff(bin) * 100
                    data_group.add_value("eff", eff, is_bold=True)
                    graph_values[data_key][np].append((bin, eff))

            print tab.texify()

        for np in pdg.VALID_UPS_DECAYS[ns]:
            graphs = []
            for data_key in ["mc2011", "mc2012"]:
                g = graph.Graph(color=data_key,
                                values=graph_values[data_key][np], space=3)
                graphs.append(g)
            mg = graph.MultiGraph(graphs=graphs, ymin=0)
            mg.draw()

            output = "mc/eff/ups%d_%d" % (ns, np)
            tools.save_figure(output)

            # h = (graphs[0].h + graphs[1].h) / 2
            # h.Fit("pol0")
            # h.Draw()
            # output = "mc/eff/ups%d_%d_fit" % (ns, np)
            # tools.save_figure(output)


if __name__ == '__main__':
    main()
