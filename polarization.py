#!/usr/bin/env python
""" Polarization

Usage:
  polarization [-s] [--name=<name>]

Options:
  -s --save  Save results
  --name=<name>     Name of output database [default: polarization]
"""
import env  # noqa
from docopt import docopt

import tools
import pdg
# from th.model.selector import Selector
import ROOT
from ROOT import TVector3
from ROOT import TLorentzVector
from IPython import embed as shell  # noqa
from array import array
from math import cos
from math import sin
from collections import defaultdict

from AnalysisPython import LHCbStyle  # noqa
# LHCbStyle.lhcbStyle.SetOptTitle(1)
# LHCbStyle.lhcbStyle.SetTitleX(0.15)
# LHCbStyle.lhcbStyle.SetTitleY(0.92)
# LHCbStyle.lhcbStyle.SetTitleBorderSize(0)
# LHCbStyle.lhcbStyle.SetTitleFillColor(0)

import PyRoUts as pyroot

class Columns(object):

    def __init__(self, chain):
        self.columns = {}
        for c in chain.GetListOfBranches():
            self.columns[c.GetName()] = array('d', [0])
            chain.SetBranchAddress(c.GetName(), self.columns[c.GetName()])

    def __getitem__(self, key):
        return self.columns[key][0]


def register_branches(chain):
    columns = {}
    for c in chain.GetListOfBranches():
        columns[c.GetName()] = array('d', [0])
        chain.SetBranchAddress(c.GetName(), columns[c.GetName()])
    return columns


def col(arr, name):
    return arr[name][0]


def angles(cols):
    v_chib = TVector3(cols["px_cb"], cols["py_cb"], cols["pz_cb"])

    # for boosting to chib lab
    v_bchib = TVector3(
        -cols["px_cb"] / cols["e_chib"],
        -cols["py_cb"] / cols["e_chib"],
        -cols["pz_cb"] / cols["e_chib"]
    )
    # v_ups = TVector3(px_y, py_y, pz_y)

    # boosting
    lv_ups = TLorentzVector(
        cols["px_y"],
        cols["py_y"],
        cols["pz_y"],
        cols["e_y"]
    )
    lv_mup = TLorentzVector(
        cols["px_mup"],
        cols["py_mup"],
        cols["pz_mup"],
        cols["e_mup"]
    )
    lv_mum = TLorentzVector(
        cols["px_mum"],
        cols["py_mum"],
        cols["pz_mum"],
        cols["e_mum"]
    )

    lv_ups.Boost(v_bchib)
    lv_mup.Boost(v_bchib)
    lv_mum.Boost(v_bchib)

    v_ups_chib = TVector3(
        lv_ups.Px(), lv_ups.Py(), lv_ups.Pz())
    v_mup_chib = TVector3(
        lv_mup.Px(), lv_mup.Py(), lv_mup.Pz())
    v_mum_chib = TVector3(
        lv_mum.Px(), lv_mum.Py(), lv_mum.Pz())

    # First result
    theta = v_ups_chib.Angle(v_chib)
    # print cos(theta_chib), lv

    n_chib = v_chib.Unit()
    n_ups = v_ups_chib.Unit()
    n_mup = v_mup_chib.Unit()
    n_mum = v_mum_chib.Unit()

    n_perp_ups = n_mup.Cross(n_mum).Unit()
    n_perp_chib = n_ups.Cross(n_chib).Unit()

    cosphi = n_perp_chib.Dot(n_perp_ups)

    v_bups = TVector3(-lv_ups.Px() / lv_ups.E(),
                      -lv_ups.Py() / lv_ups.E(),
                      -lv_ups.Pz() / lv_ups.E())
    lv_mup.Boost(v_bups)
    lv_mum.Boost(v_bups)

    thetap = lv_mup.Angle(v_ups_chib)

    return theta, thetap, cosphi


def get_weights(j, theta, thetap, cosphi):
    costheta = cos(theta)
    costhetap = cos(thetap)
    c2 = costheta ** 2
    cp2 = costhetap ** 2
    s2th = sin(2 * theta)
    s2thp = sin(2 * thetap)

    # print thetap, thetam
    w0 = w1 = w2 = 0
    if j == 1:
        w0 = 0.5 - 0.5 * cp2 + cp2 * c2 - \
            0.25 * s2th * s2thp * cosphi
        w1 = 0.5 - 0.5 * cp2 * c2 + \
            0.125 * s2th * s2thp * cosphi
        return w0, w1, None
    else:  # nb == 2
        c4 = c2 * c2
        c2phi = 2 * cosphi * cosphi - 1
        sinthetap = sin(thetap)
        sp2 = sinthetap ** 2
        # sintheta = sin(theta)
        # s2 = sintheta ** 2

        w0 = (0.25 + 0.3 * c2 - 0.45 * c4 + 0.25 * cp2 -
              1.5 * c2 * cp2 + 1.35 * c4 * cp2
              - 0.15 * sp2 * c2phi)
        w0 += (0.6 * c2 * sp2 * c2phi
               - 0.45 * c4 * sp2 * c2phi +
               0.3 * s2th * s2thp * cosphi - 0.45 *
               c2 * s2th * s2thp * cosphi)

        w1 = (0.3 - 0.3 * c2 + 0.3 * c4 +
              0.6 * c2 * cp2 - 0.9 * c4 * cp2)
        w1 += (-0.3 * c2 * sp2 * c2phi +
               0.3 * c4 * sp2 * c2phi -
               0.075 * s2th * s2thp * cosphi +
               0.3 * c2 * s2th * s2thp * cosphi)

        w2 = (0.225 + 0.15 * c2 - 0.075 * c4 -
              0.075 * cp2 + 0.15 * c2 * cp2 +
              0.225 * c4 * cp2 + 0.075 * sp2 * c2phi
              )
        w2 += (-0.075 * c4 * sp2 * c2phi - 0.075 * s2th *
               s2thp * cosphi -
               0.075 * c2 * s2th * s2thp * cosphi)
        return w0, w1, w2


def process(ns, nb, np, chain, cut, axis):
    # w3 - from simulation (unpolarized)
    histos = []
    hangles = defaultdict(list)
    cols = Columns(chain=chain)

    for w in range(4):
        h = pyroot.h1_axis(axis=axis)
            # title="w%d; p_{T}^{#Upsilon(%dS)};events" % (w, ns))
        h.Sumw2()
        histos.append(h)

    for a in ["theta", "thetap", "cosphi"]:
        for w in range(4):
            x0, x1 = (-1, 1) if a != "theta" else (-1, 0)
            h = ROOT.TH1D(pyroot.hID(), "{angle}".format(angle=a), 100, x0, x1)
            h.Sumw2()
            h.red() if w != 3 else h.blue()
            hangles[a].append(h)

    list_id = pyroot.rootID()

    new_cut = dict(cut)
    new_cut["nb"], new_cut["np"] = nb, np
    cut_str = tools.cut_dict2str(new_cut)
    print chain.GetName(), "Cut: ", cut_str
    chain.Draw(">>%s" % list_id, cut_str, "entrylist")
    entry_list = ROOT.gROOT.FindObject(list_id)
    print "Entry list", entry_list.GetN()
    print "Start reweigting..."

    for i in range(entry_list.GetN()):
        chain.GetEntry(entry_list.GetEntry(i))
        theta, thetap, cosphi = angles(cols)
        weights = get_weights(nb, theta, thetap, cosphi)

        for i, w in enumerate(weights):
            if w:
                histos[i].Fill(cols["pt_ups"], w)
                hangles["theta"][i].Fill(cos(theta), w)
                hangles["thetap"][i].Fill(cos(thetap), w)
                hangles["cosphi"][i].Fill(cosphi, w)

        histos[3].Fill(cols["pt_ups"])
        hangles["theta"][3].Fill(cos(theta))
        hangles["thetap"][3].Fill(cos(thetap))
        hangles["cosphi"][3].Fill(cosphi)

    print "End"
    return histos, hangles


def save(data_key, ns, np, nb, hists, d, n):
    db = tools.get_db("polarization")
    data = db.get(data_key, {})
    ups_key = "ups%ds" % ns
    ups = data.get(ups_key, {})

    binning = []
    for ibin in hists[0]:
        binning.append(
            (int(hists[0].GetBinLowEdge(ibin)),
             int(hists[0].GetBinLowEdge(ibin)) +
             int(hists[0].GetBinWidth(ibin))
             )
        )
    for i in range(4):
        for ibin, pt_bin in enumerate(binning, start=1):
            bin = ups.get(pt_bin, {})
            chib_key = "chib%d%dp" % (nb, np)
            chib = bin.get(chib_key, {})
            if i < len(hists):
                w_key = "w%d" % i
                chib[w_key] = (hists[i][ibin].value(), hists[i][ibin].error())

            d_key = "d%d" % i
            n_key = "n%d" % i
            chib[d_key] = (d[i][ibin].value(), d[i][ibin].error())
            chib[n_key] = (n[i][ibin].value(), n[i][ibin].error())

            bin[chib_key] = chib
            ups[pt_bin] = bin

    data[ups_key] = ups
    db[data_key] = data
    db.close()


def main():
    cli_args = docopt(__doc__, version='v1.0')

    cfg_tuples = tools.load_config("tuples")
    cfg_pol = tools.load_config("polarization")
    chib_chain = ROOT.TChain("ChibAlg/Chib")
    ups_chain = ROOT.TChain("UpsilonAlg/Upsilon")
    cfg_decays = tools.load_config("mc")["decays"]
    # ups_chain = ROOT.TChain("UpsilonAlg/Upsilon")

    name = cli_args["--name"]
    for data_key in cfg_pol["data_keys"]:
        save_to = "{name}/{data_key}/".format(name=name, data_key=data_key)
        chib_chain.Reset()
        ups_chain.Reset()
        for ntuple_file in cfg_tuples[data_key]:
            print "NTuple ", ntuple_file
            chib_chain.Add(ntuple_file)
            ups_chain.Add(ntuple_file)

        for ns in cfg_pol["ns"]:
            cfg_cuts = cfg_decays["ups%ds" % ns]
            chib_cut = cfg_cuts["cut"]
            ups_cut = cfg_cuts["ucut"]
            # tools.tree_preselect(chib_chain, chib_cut)
            # tools.tree_preselect(ups_chain, ups_cut)
            for np in cfg_pol["np"]:
                if np not in pdg.VALID_UPS_DECAYS[ns]:
                    continue

                axis = cfg_pol["axis"]["ups%ds" % ns][str(np)]

                for nb in cfg_pol["nb"]:

                    d, dangles = process(ns=ns, nb=nb, np=np, chain=chib_chain,
                                         cut=chib_cut, axis=axis)
                    n, nangles = process(ns=ns, nb=nb, np=np, chain=ups_chain,
                                         cut=ups_cut, axis=axis)
                    ref = d[3] // n[3]
                    res = []

                    for i in range(3):
                        if nb == 1 and i > 1:
                            continue
                        h = ref / (d[i] // n[i])
                        h.red()

                        res.append(h)

                        h.Draw()
                        h.level(1)

                        tools.save_figure(
                            name=(save_to +
                                  "chib{nb}{np}p_ups{ns}s_w{w}_ratio"
                                  .format(nb=nb, np=np, ns=ns, w=i))
                        )
                    for angle in dangles:
                        hunpol = dangles[angle][3]
                        hunpol.scale()

                        for i in range(0, 3):
                            h = dangles[angle][i]
                            if not h.GetEntries():
                                continue
                            h.scale()
                            wname = "w%d" % i
                            tools.draw_hists([h, hunpol], minimum=0)
                            if cli_args['--save']:
                                tools.save_figure(
                                    save_to +
                                    "/angles/{wname}_{angle}_chib{nb}{np}p_ups{ns}s".format(
                                        wname=wname, angle=angle, nb=nb, np=np, ns=ns)
                                )
                    if cli_args['--save']:
                        save(data_key, ns, np, nb, res,  d, n)
            # chib_chain.SetEntryList(0)
            # ups_chain.SetEntryList(0)
    shell()
                # shell()
if __name__ == '__main__':
    main()
