#!/usr/bin/env python

from IPython import embed as shell
import tools


import AnalysisPython.PyRoUts as pyroot
VE = pyroot.VE

from AnalysisPython import LHCbStyle  # noqa


def main():
    cfg = tools.load_config("rep_width_data_mc")

    axis = cfg["axis"]
    binning = tools.axis2bins(axis)
    db_mc = tools.get_db(cfg["mc"], 'r')
    db_data = tools.get_db(cfg["data"], 'r')

    for year in ["2011", "2012"]:
        h_mc = pyroot.h1_axis(axis)
        h_mc.red()
        h_data = pyroot.h1_axis(axis)
        h_data.blue()

        db_mc_year = db_mc["mc%s" % year]["ups1s"]
        db_data_year = db_data[year]

        for i, bin in enumerate(binning, start=1):
            h_mc[i] = VE(str(db_mc_year[bin]['chib11p']['sigma']))
            h_data[i] = VE(str(db_data_year[bin]['sigma_b1_1p']))

        h_ratio = h_data / h_mc
        h_ratio.Draw()
        h_ratio.Fit("pol0")
        tools.save_figure("%s/sigma_data_mc_%s" % (cfg["output_dir"], year))
        shell()

if __name__ == '__main__':
    main()
