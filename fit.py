#!/usr/bin/env python
# Usage: th fit
# Summary: Fit models
# Help: th fit -h

"""Fit.

Usage:
  fit --complete
  fit [-i] --decay=<decay> --year=<year>
       --ptbegin=<ptbegin>
       --ptend=<ptend>
       [--profile=<profile>]

Options:
  -i --interactive  Run ipython shell
  -h --help     Show this screen.
"""

import env

from docopt import docopt

import shelve
import ROOT
import pprint
from AnalysisPython import LHCbStyle  # noqa

import tools
from log import Logger
import source

from IPython import embed as shell


# def get_cli_args():
#     parser = argparse.ArgumentParser(description='Process some integers.')
#     parser.add_argument(
#         '--complete', help='Show completion list', action='store_true')
#     parser.add_argument(
#         '-i', "--interective", help='Interective session',
#         action='store_true')
#     parser.add_argument(
#         '--decay', help='Decay name', choices=['ups', '1s', '2s', '3s'])
#     parser.add_argument(
#         '--profile', help='Update default properties')
#     parser.add_argument(
#         '--year', help='Show completion list',
#         choices=['all', '2011', '2012'])
#     parser.add_argument(
#         '--ptbegin', help='Start p_T', type=int)
#     parser.add_argument(
#         '--ptend', help='End p_T', type=int)
#     return parser.parse_args()


def get_fitter(name):
    if name == "ups":
        import ups_fit
        return ups_fit

    if name == "chib1s":
        import chib1s_fit
        return chib1s_fit
    return None


def complete():
    print "--decay=ups"
    print "--decay=1s"
    print "--decay=2s"
    print "--decay=3s"
    print "--year"
    print "--ptbegin"
    print "--ptend"


def save(name, model, year, interval):
    db_path = "data/%s.db" % name
    tools.create_path(db_path)

    db = shelve.open(db_path)

    db_year = db.get(year, {})
    db_year[interval] = model.params()
    db[year] = db_year

    print db
    db.close()

    figure = "{name}/f{year}_{pt1}_{pt2}".format(
        name=name, year=year, pt1=interval[0], pt2=interval[1])

    tools.save_figure(figure, model.canvas)


def main():
    cli_args = docopt(__doc__, version='v1.0')

    def fit():
        model.fitData()
        print(model)

        if cfg['save?']:
            save(cfg['name'], model, cli_args["--year"],
                 (int(cli_args["--ptbegin"]), int(cli_args["--ptend"])))

        if model.status:
            log.info("OK")
        else:
            log.err("BAD")

    log = Logger()
    # cli_args = get_cli_args()
    if cli_args["--complete"]:
        complete()
        exit(0)
    tuples_cfg = tools.load_config("tuples")

    if cli_args["--year"]:
        tuples = [tuples_cfg[cli_args["--year"]]]
    else:  # all
        tuples = [tuples_cfg[year] for year in ['2011', '2012']]

    cfg = tools.load_config(cli_args["--decay"])
    tree = ROOT.TChain(cfg["tree"])
    for file_name in tuples:
        tree.Add(file_name)

    fitter = get_fitter(cli_args["--decay"])
    canvas = ROOT.TCanvas("c_fit",
                          "{year} {start}-{end} {name}".format(
                              year=cli_args["--year"],
                              start=cli_args["--ptbegin"],
                              end=cli_args["--ptend"],
                              name=cfg["name"])
                          )
    cut = cfg['cut']
    cut["pt_ups"] = (int(cli_args["--ptbegin"]), int(cli_args["--ptend"]))

    log.info("Cut: %s" % tools.cut_dict2str(cfg['cut']))

    if cfg["unbinned?"]:
        data = source.dataset(tree=tree,
                              cut=cut,
                              field=cfg['field'],
                              has_splot=cfg['splot?'])
    else:
        data = source.histogram(tree=tree,
                                cut=cut,
                                field=cfg['field'],
                                nbins=cfg['nbins'])

    # Use 2012 MC if we fit joined datasset
    mc_year = cli_args["--year"] if cli_args["--year"] != "all" else "2012"
    mc = tools.get_db(tuples_cfg["mc"], "r")["mc%s" % mc_year]["ups1s"]

    new_cfg = dict(cfg)
    new_cfg.update(cfg['profiles'].get(cli_args["--profile"], {}))
    del new_cfg["profiles"]

    log.info("Profile:" + pprint.pformat(new_cfg, indent=2))
    model = fitter.prepare_model(
        canvas=canvas,
        data=data,
        mc=mc,
        interval=cfg['cut'][cfg['field']],
        nbins=cfg['nbins'],
        name=cfg['name'],
        has_splot=cfg['splot?'],
        profile=new_cfg,
        pt_ups=cut["pt_ups"]
    )

    fit()

    if cli_args["--interactive"] or not model.status:
        shell()

if __name__ == '__main__':
    main()
