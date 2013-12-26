#!/usr/bin/env python
from IPython import embed as shell

import env  # noqa
# import graph
import tools
import pdg

import AnalysisPython.PyRoUts as pyroot
VE = pyroot.VE


def main():
    cfg = tools.load_config("rep_graph_mc")
    db = tools.get_db(cfg["db"], 'r')

    for ns in range(1, 3):
        ups_key = "ups%ds" % ns
        axis = cfg[ups_key]['axis']
        binning = tools.axis2bins(axis)

        for data_key in ["mc2011", "mc2012"]:
            print data_key
            db_ups = db[data_key][ups_key]
            hists = [pyroot.h1_axis(axis), pyroot.h1_axis(axis)]
            for i, bin in enumerate(binning, start=1):
                sigmas = []
                for np in pdg.VALID_UPS_DECAYS[ns]:
                    chib_key = 'chib1%dp' % np
                    sigmas.append(db_ups[bin][chib_key]['sigma'])
                sigma = VE(str(sigmas[0]))
                for j, s in enumerate(sigmas[1:]):
                    hists[j][i] = VE(str(s)) / sigma
            shell()


if __name__ == '__main__':
    main()
