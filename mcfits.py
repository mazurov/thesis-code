#!/usr/bin/env python

""" MC fits
Usage:
    mcfits.py [-i] [-s] [-u] --data=<data> [--ns=<ns>] [--nb=<nb>] [--np=<np>]
"""
# =============================================================================
# Imports
# =============================================================================
# External
# =============================================================================
import env  # noqa @UnusedImport
from docopt import docopt
from IPython import embed as shell  # noqa
# =============================================================================
# ROOT
# =============================================================================
import ROOT
from AnalysisPython import LHCbStyle  # noqa
import AnalysisPython.PyRoUts as pyroot
# =============================================================================
# Local
# ============================================================================
import tools
from log import Logger
import source


import chib1s_mc_model
import chib2s_mc_model
import chib3s_mc_model
# ============================================================================

canvas = ROOT.TCanvas("c_mcfits", "mcfits", 800, 600)


def get_model(klass, np, binning):
    return klass(canvas=canvas, p=np, binning=binning)


def save(name, data_key, params, ns, nb, np, pt_bin):
    db = tools.get_db(name)
    data = db.get(data_key, {})
    ups_key = "ups%ds" % ns
    ups = data.get(ups_key, {})
    bin = ups.get(pt_bin, {})
    chib_key = "chib%d%dp" % (nb, np)
    bin[chib_key] = params

    ups[pt_bin] = bin
    data[ups_key] = ups
    db[data_key] = data
    db.close()

    figure = "{name}/{data_key}/{ups_key}/{chib_key}/f_{pt1}_{pt2}".format(
        name=name, data_key=data_key, ups_key=ups_key, chib_key=chib_key,
        pt1=pt_bin[0], pt2=pt_bin[1]
    )
    tools.save_figure(figure, canvas=canvas)


def usave(name, data_key, ns, nb, np, h):
    db = tools.get_db(name)
    data = db.get(data_key, {})
    ups_key = "ups%ds" % ns
    ups = data.get(ups_key, {})
    for i in h:
        pt_bin = (int(h.GetBinLowEdge(i)),
                  int(h.GetBinLowEdge(i) + h.GetBinWidth(i)))
        bin = ups.get(pt_bin, {})
        val_key = "ups_chib%d%dp" % (nb, np)
        bin[val_key] = (h[i].value(), h[i].error())
        ups[pt_bin] = bin
        data[ups_key] = ups
        db[data_key] = data

    db.close()


def count_upsilons(name, data_key, tree, ns, nb, np, pt_axis, cut, is_save):
    new_cut = dict(cut)
    h = pyroot.h1_axis(axis=pt_axis)
    new_cut.update({
        "nb": nb,
        "np": np
    })
    tree.Draw("pt_ups>>%s" % h.GetName(), tools.cut_dict2str(new_cut))
    if is_save:
        usave(name, data_key, ns, nb, np, h)


def process(
    name, data_key, tree, models, ns, nb, np, cut, pt_axis, is_unbinned,
        binning, is_save):
    def fit():
        model.fitData()
        print model
        if is_save:
            save(
                name=name, data_key=data_key, params=model.params(), ns=ns,
                nb=nb, np=np, pt_bin=pt_bin
            )
        if model.status:
            log.info("OK")
        else:
            log.err("BAD")

    new_cut = dict(cut)
    field = "dmplusm%ds" % ns
    new_cut[field] = tuple(binning[1:])
    new_cut["np"] = np
    new_cut["nb"] = nb

    log = Logger()
    list_id = pyroot.rootID()
    cut_str = tools.cut_dict2str(new_cut)

    log.info("cut:" + cut_str)
    tree.Draw(">>%s" % list_id, cut_str, "entrylist")
    elist = ROOT.gROOT.FindObject(list_id)
    tree.SetEntryList(elist)

    model = get_model(models[ns - 1], np, binning)
    for pt_bin in tools.axis2bins(pt_axis):
        bin_cut = {"pt_ups": pt_bin}
        if is_unbinned:
            data = source.dataset(tree=tree, cut=bin_cut, field=field,
                                  has_splot=False)
        else:
            data = source.histogram(tree=tree,
                                    cut=bin_cut,
                                    field=field,
                                    nbins=binning[0])
        model.data = data
        canvas.SetTitle(
            "%s: chib%d%dp to Y(%dS) (%d, %d) " % (data_key, nb, np, ns,
                                                   pt_bin[0], pt_bin[1]))

        fit()
        if not model.status:
            shell()
    tree.SetEntryList(0)


def main():
    cli_args = docopt(__doc__, version="1.0")
    args = dict(cli_args)

    log = Logger()
    models = [
        chib1s_mc_model.ChibMCModel,
        chib2s_mc_model.ChibMCModel,
        chib3s_mc_model.ChibMCModel,
    ]
    tuples_cfg = tools.load_config("tuples")
    mc_cfg = tools.load_config("mc")

    tree = ROOT.TChain("ChibAlg/Chib")
    utree = ROOT.TChain("UpsilonAlg/Upsilon")

    tree.Add(tuples_cfg[args["--data"]])
    utree.Add(tuples_cfg[args["--data"]])

    # TODO: create arrays with respect to ns
    if not args["--ns"]:
        ns_arr = [1, 2, 3]
    else:
        ns_arr = [int(args["--ns"])]

    if not args["--np"]:
        np_arr = [1, 2, 3]
    else:
        np_arr = [int(args["--np"])]
    if not args["--nb"]:
        nb_arr = [1, 2]
    else:
        nb_arr = [int(args["--nb"])]

    for ns in ns_arr:
        decay_cfg = mc_cfg["decays"]["ups%ds" % ns]
        for np in np_arr:
            for nb in nb_arr:
                if (ns == 2 and np == 1) or (ns == 3 and np < 3):
                    continue
                process(
                    name=mc_cfg["name"],
                    data_key=args["--data"],
                    tree=tree,
                    models=models,
                    ns=ns,
                    np=np,
                    nb=nb,
                    cut=decay_cfg["cut"],
                    pt_axis=decay_cfg["axis"],
                    is_unbinned=mc_cfg["unbinned?"],
                    binning=decay_cfg["binning"]["%d" % np],
                    is_save=args["-s"]
                )

                if args["-u"]:
                    count_upsilons(
                        name=mc_cfg["name"], data_key=args["--data"],
                        tree=utree, ns=ns, nb=nb, np=np,
                        pt_axis=decay_cfg["axis"],
                        cut=decay_cfg["ucut"], is_save=args["-s"])

    if args['-i']:
        db = tools.get_db(mc_cfg["name"])
        print db.keys
        shell()


if __name__ == '__main__':
    main()
