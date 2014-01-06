#!/usr/bin/env python

""" Fraction report.

Usage:
  rep_frac.py --profile=<profile>

Options:
  --profile=<profile>   Report profile

"""


import tools
import table
import graph
import mctools

from AnalysisPython.PyRoUts import VE

from docopt import docopt
from collections import defaultdict
from IPython import embed as shell  # noqa


def main():
    cli_args = docopt(__doc__, version='v1.0')
    cfg = tools.load_config("rep_frac")

    profile_name = cli_args["--profile"]
    profile_cfg = cfg[profile_name]
    ns = profile_cfg["ns"]

    db = tools.get_db(profile_cfg["db"], "r")
    db_y = tools.get_db(profile_cfg["db_y"], "r")
    db_mc = tools.get_db(profile_cfg["mc"], "r")

    # table
    bins = set()
    axis_bins = {}
    axises = profile_cfg["axises"]
    for np in axises:
        axis_bins[int(np)] = tools.axis2bins(axises[np])
        bins.update(axis_bins[int(np)])
    bins = sorted(bins)

    tab = table.SqsTable(
        title=profile_cfg["title"],
        label=profile_cfg["label"],
        ns=ns,
        binning=bins,
        scale=profile_cfg["scale"],
        maxbins=profile_cfg["maxbins"]
    )

    for np in profile_cfg["nps"]:
        tab.add_row(
            key=str(np),
            title=r"$N_{\chi_b(%dP)}$" % np
        )
    tab.space()
    tab.add_row(key="y", title=r"$N_{\Upsilon(%dS)}$" % ns)
    tab.space()
    for np in profile_cfg["nps"]:
        title = (r"$\eps_{\chi_b(%dP) \to \Upsilon(%dS)" % (np, ns) +
                 r" \gamma}^{\gamma}$, \%")
        tab.add_row(
            key="e%d" % np,
            title=title
        )
    tab.line()
    for np in profile_cfg["nps"]:
        tab.add_row(
            key="f%d" % np,
            title=r"Fraction $\chi_b(%dP)$, \%%" % np
        )

    values = {
        "2011": defaultdict(list),
        "2012": defaultdict(list),
    }
    for bin in bins:
        for data_key in ["2011", "2012"]:
            bin_group = tab.get_group(bin, data_key)
            db_bin = db[data_key][bin]
            db_y_bin = db_y[data_key][bin]

            ups_key = "N%dS" % ns
            nups = db_y_bin.get(ups_key, None)
            bin_group.add_value(key="y", value=nups)

            for np in profile_cfg["nps"]:
                mct = mctools.MC(
                    db=db_mc["mc%s" % data_key]["ups%ds" % ns],
                    ns=profile_cfg["ns"],
                    np=np
                )
                key = "N%sP" % np
                nchib = db_bin.get(key, None)
                bin_group.add_value(key=str(np), value=nchib)

                eff = mct.eff(bin)
                bin_group.add_value(key="e%d" % np, value=eff * 100)

                if nups and nchib and eff and (bin in axis_bins[np]):
                    frac = (VE(str(nchib)) / VE(str(eff))
                            / VE(str(nups))) * 100
                    values[data_key][np].append((bin, frac))
                else:
                    frac = None

                bin_group.add_value(key="f%d" % np, value=frac, is_bold=True)

    print tab.texify()

    graphs_cfg = profile_cfg["graphs"]
    for np in profile_cfg["nps"]:
        graphs = []
        for data_key in ["2011", "2012"]:
            graph_values = values[data_key][np]
            if graph_values[0][0] != 0:
                graph_values.insert(0, ((0, graph_values[0][0]), None))
            g = graph.Graph(color=data_key, values=values[data_key][np])
            graphs.append(g)

        ymax = graphs_cfg[str(np)]["ymax"]

        if ns == 1 and np == 1:
            g = graph.Graph(color="2010", values=profile_cfg["2010"])
            graphs.append(g)

        mg = graph.MultiGraph(graphs=graphs, ymin=0, ymax=ymax)

        mg.draw()

        output_file = "fracs/%s_%d" % (profile_name, np)
        tools.save_figure(output_file)


if __name__ == '__main__':
    main()
