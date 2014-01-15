#!/usr/bin/env python
import ROOT

import ups_mc_model
UpsMCModel = ups_mc_model.UpsMCModel

import tools

from IPython import embed as shell  # noqa


def main():
    canvas = ROOT.TCanvas("c_ups", "c_ups", 800, 600)
    cfg = tools.load_config("mc")
    cfg_tuples = tools.load_config("tuples")

    utree = ROOT.TChain("UpsilonAlg/Upsilon")
    utree.Add(cfg_tuples["mc2011"][0])
    cut = cfg["decays"]["ups1s"]["ucut"]
    cut["pt_ups"] = [14, 18]
    cut_str = tools.cut_dict2str(cut)

    h = ROOT.TH1D("h_ups", "h_ups", 100, 9.2, 9.7)
    utree.Draw("m_dtf>>%s" % h.GetName(), cut_str)

    model = UpsMCModel(
        canvas=canvas,
        data=h,
        binning=[100, 9.2, 9.7],

    )
    model.fitData()
    print(model)
    shell()

if __name__ == '__main__':
    main()
