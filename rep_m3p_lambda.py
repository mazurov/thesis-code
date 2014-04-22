#!/usr/bin/env python

import env  # noqa
import tools
from AnalysisPython import LHCbStyle  # noqa
import AnalysisPython.PyRoUts as pyroot
import dbtools
import shelve

from IPython import embed as shell  # noqa


def main():
    axis = list(tools.drange(-0.05, 1.05, 0.1))
    hists = []
    for m in ["mass", "mass10"]:
        h = pyroot.h1_axis(axis=axis)
        h.blue() if m == "mass" else h.red()
        for i, l in enumerate(range(0, 11), start=1):

            db = shelve.open("data/ups3s/%s/lambda%d.db" % (m, l), "r")
            mass = dbtools.get_db_param(
                db=db,
                param="mean_b1_3p",
                year="all",
                bin=(24, 40))
            h[i] = mass
        
        if m == "mass10":
            g = h.asGraph3(0.01)
            for j in g:
                g.SetPointEXhigh(j, 0)
                g.SetPointEXlow(j, 0)
            g.Draw("P")
            hists.append(g)
        else:
            h.Draw("e1x0")
            hists.append(h)
    tools.save_figure("ups3s/m3p_lambda")

if __name__ == '__main__':
    main()
