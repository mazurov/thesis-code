#!/usr/bin/env python

import tools
import table
import pdg
import dbtools

from IPython import embed as shell  # noqa


def collect(cfg_pol):
    data_key = cfg_pol['data_key']
    db_pol = tools.get_db(cfg_pol['db'], "r")[data_key]

    ret = {}
    for ns in range(1, 4):
        ups_key = "ups%ds" % ns
        ret[ups_key] = {}
        for np in pdg.VALID_UPS_DECAYS[ns]:
            binning = tools.axis2bins(
                tools.get_axis(np, cfg_pol['axis'][ups_key][str(np)])
            )
            chip_key = "chib%dp" % np
            ret[ups_key][chip_key] = {}
            for bin in binning:
                plus, minus = dbtools.get_polarization_change(
                    db_pol, ns, np, bin
                )
                ret[ups_key][chip_key][bin] = (plus * 100, minus * 100)
    return ret


def publish(ret, cfg_pol):

    for ns in range(1, 4):
        ups_key = "ups%ds" % ns
        ups = ret[ups_key]

        title = cfg_pol['title'].format(ns=ns)
        label = cfg_pol['label'].format(ns=ns)
        bins = tools.axis2bins(cfg_pol['axis'][ups_key].values())
        tab = table.PtTable(title=title, label=label, ns=ns,
                            binning=bins, maxbins=cfg_pol["maxbins"],
                            scale=cfg_pol["scale"],
                            is_cmidrule=False)
        for np in pdg.VALID_UPS_DECAYS[ns]:
            row_title = cfg_pol["row_title"].format(np=np, ns=ns)
            tab.add_row(str(np), row_title)
            if np != pdg.VALID_UPS_DECAYS[ns][-1]:
                tab.space()

            chip_key = "chib%dp" % np
            chip = ups[chip_key]
            valid_bins = tools.axis2bins(cfg_pol['axis'][ups_key][str(np)])

            for bin in bins:
                cell = tab.get_bin(bin)
                if bin in valid_bins:
                    value = (
                        "${}^{+%.1f}_{-%.1f}$" % (chip[bin][0], chip[bin][1])
                    )
                else:
                    value = None
                cell.add_value(key=str(np), value=value)

        print tab.texify()

if __name__ == '__main__':
    cfg_pol = tools.load_config('rep_pol')
    ret = collect(cfg_pol)
    publish(ret, cfg_pol)
