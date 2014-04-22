#!/usr/bin/env python

""" Yields report.

Usage:
  ./rep_yields.py --profile=<profile>

Options:
  --profile=<profile> Report profile
"""
import env
import tools
import graph
from docopt import docopt

import ROOT
from AnalysisPython.PyRoUts import VE

from IPython import embed as shell  # noqa


def main():
    cli_args = docopt(__doc__, version='v1.0')
    canvas = ROOT.TCanvas("c_yields", "c_yields", 800, 600)

    cfg = tools.load_config("rep_yields")

    report_key = cli_args["--profile"]

    report_cfg = cfg[report_key]
    db = tools.get_db(report_cfg["db"])
    output_dir = report_cfg["output_dir"]

    plots_cfg = report_cfg["plots"]
    for plot_cfg in plots_cfg:
        yield_key = plot_cfg["key"]
        bins = tools.axis2bins(plot_cfg["axis"])

        graphs = []
        graphs_scaledbybin = []
        graphs_scaledbylum = []

        for data_key in ["2011", "2012"]:
            values = []
            values_scaledbybinsize = []
            values_scaledbylum = []
            for bin in bins:
                if bin in db[data_key]:
                    value = VE(str(db[data_key][bin][yield_key]))
                    values.append((bin, value))
                    value_bin = value / (bin[1] - bin[0])

                    values_scaledbybinsize.append((bin, value_bin))
                    scale = 1 if data_key == "2011" else 2
                    values_scaledbylum.append((bin, value_bin / scale))
                else:
                    values.append((bin, None))
                    values_scaledbybinsize.append((bin, None))
                    values_scaledbylum.append((bin, None))

            graphs.append(
                graph.Graph(color=data_key, values=values)
            )

            graphs_scaledbybin.append(
                graph.Graph(color=data_key,
                            values=values_scaledbybinsize)
            )
            graphs_scaledbylum.append(
                graph.Graph(color=data_key, values=values_scaledbylum)
            )

        ymin = plot_cfg["ymin"]
        ymax = plot_cfg["ymax"]

        if plot_cfg.get("logscale?", False):
            canvas.SetLogy(True)
        else:
            canvas.SetLogy(False)

        mg = graph.MultiGraph(graphs=graphs, ymin=ymin[0], ymax=ymax[0])
        mg.draw()
        tools.save_figure("%s/%s" % (output_dir, yield_key))

        mg = graph.MultiGraph(graphs=graphs_scaledbybin, ymin=ymin[1],
                              ymax=ymax[1])
        mg.draw()
        tools.save_figure("%s/%s_scaledbybin" % (output_dir, yield_key))
        mg = graph.MultiGraph(graphs=graphs_scaledbylum, ymin=ymin[2],
                              ymax=ymax[2])
        mg.draw()

        tools.save_figure("%s/%s_scaledbylum" % (output_dir, yield_key))
        canvas.SetLogy(False)

if __name__ == '__main__':
    main()
