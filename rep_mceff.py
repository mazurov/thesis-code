#!/usr/bin/env python

from IPython import embed as shell  # noqa

import tools
import mctools
import pdg

import table


def process(db_name, data_key, ns, np):
    # mc = mctools.MC(db_name, data_key, ns, np)

    # for nb in range(1,3):
    pass


def create_table(label, title, scale, cfg_rows, ns, np, binning, maxbins):
    tab = table.PtTable(
        title=title,
        label=label,
        ns=ns,
        binning=binning,
        scale=scale,
        maxbins=maxbins
    )

    for nb in range(1, 3):
        for i in range(3):
            key = cfg_rows[i]["key"].format(nb=nb, np=np, ns=ns)
            title = cfg_rows[i]["title"].format(nb=nb, np=np, ns=ns)
            tab.add_row(key=key, title=title)
        tab.space()
    tab.line()
    tab.add_row(key=cfg_rows[3]["key"], title=cfg_rows[3]["title"])
    return tab


def main():
    cfg_rep = tools.load_config("rep_mceff")
    cfg_mc = tools.load_config("mc")

    db = tools.get_db(cfg_rep["db"], "r")

    for ns in range(1, 4):
        for np in pdg.VALID_UPS_DECAYS[ns]:
            title = cfg_rep["title"].format(
                ns=ns,
                np=np
            )
            label = cfg_rep["label"].format(
                ns=ns,
                np=np
            )
            ups_key = "ups%ds" % ns
            axis = tools.get_axis(np, cfg_mc["decays"][ups_key]["axis"])

            bins = tools.axis2bins(axis)
            maxbins = cfg_rep["maxbins"]

            tab = create_table(label=label, title=title,
                               scale=cfg_rep["scale"],
                               cfg_rows=cfg_rep["rows"],
                               ns=ns, np=np, binning=bins, maxbins=maxbins)

            for bin in bins:
                for data_key in cfg_rep["data_keys"]:
                    mc = mctools.MC(db=db[data_key][ups_key], ns=ns, np=np)
                    bin_group = tab.get_bin(bin)
                    data_group = bin_group.add_subgroup(
                        data_key,
                        data_key
                    )
                    for nb in range(1, 3):
                        data_group.add_value("n%d" % nb,
                                             mc.nchib(bin, nb))
                        data_group.add_value("nups%d" % nb,
                                             mc.nups(bin, nb))
                        data_group.add_value("eff%d" % nb,
                                             mc.eff(bin, nb) * 100,
                                             is_bold=True)
                    data_group.add_value("eff", mc.eff(bin) * 100,
                                         is_bold=True)

            print tab.texify()


if __name__ == '__main__':
    main()
