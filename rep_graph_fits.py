#!/usr/bin/env python

""" MC fits
Usage:
    rep_graphfits.py [-i] --profile=<profile>

Options:
    -i                  Interactive
    --profile=<profile> Graph properties
"""


import env  # noqa
from docopt import docopt
from IPython import embed as shell


import tools
import graph
import AnalysisPython.PyRoUts as pyroot


def main():
    cli_args = docopt(__doc__, version="1.0")

    cfg = tools.load_config("rep_graph_fits")
    cfg_profile = cfg['profiles'][cli_args['--profile']]

    db = tools.get_db(cfg_profile['db'])
    binning = tools.axis2bins(cfg_profile['axis'])

    for plot in cfg_profile['plots']:
        key = plot['key']
        graphs = []
        for data_key in ['2011', '2012']:
            values = []
            for bin in binning:
                ve = pyroot.VE(str(db[data_key][bin][key]))
                values.append((bin, ve))
            graphs.append(graph.Graph(color=data_key, values=values))

        ymin = plot.get("ymin", None)
        ymax = plot.get("ymax", None)
        mg = graph.MultiGraph(graphs=graphs, ymin=ymin, ymax=ymax)

        mg.draw()

        level = plot.get("level", None)
        if level:
            graphs[0].h.level(level)

        filename = "%s/%s" % (cfg_profile["output_dir"], key)
        tools.save_figure(filename)
    shell()
if __name__ == '__main__':
    main()
