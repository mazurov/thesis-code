#!/usr/bin/env python

import env  # noqa
import PyRoUts as pyroot
import tools
# from th.model.selector import Selector
import ROOT
from ROOT import TVector3
from ROOT import TLorentzVector
from IPython import embed as shell  # noqa
from array import array
from math import cos
from math import sin

from AnalysisPython import LHCbStyle  # noqa
LHCbStyle.lhcbStyle.SetOptTitle(1)
LHCbStyle.lhcbStyle.SetTitleX(0.15)
LHCbStyle.lhcbStyle.SetTitleY(0.92)
LHCbStyle.lhcbStyle.SetTitleBorderSize(0)
LHCbStyle.lhcbStyle.SetTitleFillColor(0)


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
        cols["pz_cb"] / cols["e_chib"]
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

    n_perp_ups = n_mup.Cross(n_mum)
    n_perp_chib = n_ups.Cross(n_chib)

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
    cols = Columns(chain=chain)

    for w in range(4):
        h = pyroot.h1_axis(
            axis=axis,
            title="w%d; p_{T}^{#Upsilon(%dS)};events" % (w, ns))
        h.Sumw2()
        histos.append(h)

    list_id = pyroot.rootID()

    new_cut = dict(cut)
    new_cut["nb"], new_cut["np"] = nb, np
    cut_str = tools.cut_dict2str(new_cut)
    print chain.GetName(), "Cut: ", cut_str
    chain.Draw(">>%s" % list_id, cut_str, "entrylist")
    entry_list = ROOT.gROOT.FindObject(list_id)

    print "Start reweigting...",
    for i in range(entry_list.GetN()):
        chain.GetEntry(entry_list.GetEntry(i))
        theta, thetap, cosphi = angles(cols)
        weights = get_weights(nb, theta, thetap, cosphi)

        for i, w in enumerate(weights):
            if w:
                histos[i].Fill(cols["pt_ups"], w)
        histos[3].Fill(cols["pt_ups"])
    print "End"
    return histos


def save(data_key, ns, np, nb, hists):
    db = tools.get_db("polarization")
    data = db.get(data_key, {})
    ups_key = "ups%ds" % ns
    ups = data.get(ups_key, {})
    for w, hw in enumerate(hists):
        for ibin in hw:
            pt_bin = (int(hw.GetBinLowEdge(ibin)),
                      int(hw.GetBinLowEdge(ibin)) + int(hw.GetBinWidth(ibin))
                      )
            bin = ups.get(pt_bin, {})
            chib_key = "chib%d%dp" % (nb, np)
            chib = bin.get(chib_key, {})
            w_key = "w%d" % w
            chib[w_key] = (hw[ibin].value(), hw[ibin].error())
            bin[chib_key] = chib
            ups[pt_bin] = bin
    data[ups_key] = ups
    db[data_key] = data
    db.close()


def main():
    cfg_tuples = tools.load_config("tuples")
    cfg_pol = tools.load_config("polarization")
    chib_chain = ROOT.TChain("ChibAlg/Chib")
    ups_chain = ROOT.TChain("UpsilonAlg/Upsilon")
    # ups_chain = ROOT.TChain("UpsilonAlg/Upsilon")

    for data_key in cfg_pol["data_keys"]:
        chib_chain.Reset()
        ups_chain.Reset()
        for ntuple_file in cfg_tuples[data_key]:
            chib_chain.Add(ntuple_file)
            ups_chain.Add(ntuple_file)

        cfg_decays = tools.load_config("mc")["decays"]
        for ns in range(1, 4):
            cfg_cuts = cfg_decays["ups%ds" % ns]
            chib_cut = cfg_cuts["cut"]
            ups_cut = cfg_cuts["ucut"]

            for np in range(1, 4):
                if ns == 2 and np == 1:
                    continue
                if ns == 3 and (np == 1 or np == 2):
                    continue

                for nb in range(1, 3):

                    d = process(ns=ns, nb=nb, np=np, chain=chib_chain,
                                cut=chib_cut, axis=cfg_cuts["axis"])
                    n = process(ns=ns, nb=nb, np=np, chain=ups_chain,
                                cut=ups_cut, axis=cfg_cuts["axis"])
                    ref = d[3] // n[3]
                    res = []

                    for i in range(3):
                        if nb == 1 and i > 1:
                            continue
                        h = ref / (d[i] // n[i])
                        h.red()

                        h.GetYaxis().SetTitle(
                            "#varepsilon_{#gamma}^{unpol} / "
                            "#varepsilon_{#gamma}^{w%d}" % i
                        )
                        h.SetTitle("w{w}, #chi_{{b{nb}}}({np}P)"
                                   " #rightarrow #Upsilon({ns}S) #gamma"
                                   .format(nb=nb, np=np, w=i, ns=ns)
                                   )
                        res.append(h)

                        h.Draw()
                        h.level(1)

                        tools.save_figure(
                            name=("polarization/{data_key}/"
                                  .format(data_key=data_key) +
                                  "chib{nb}{np}p_ups{ns}s_w{w}_ratio"
                                  .format(nb=nb, np=np, ns=ns, w=i))
                        )
                    save(data_key, ns, np, nb, res)
    shell()
                # shell()
if __name__ == '__main__':
    main()
