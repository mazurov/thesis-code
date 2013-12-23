#!/usr/bin/env python

import tools
import table
import pdg


def collect(cfg_pol):
    cfg_mc = tools.load_config('mc')['decays']
    data_key = cfg_pol['data_key']
    db_pol = tools.get_db(cfg_pol['db'])[data_key]

    ret = {}
    for ns in range(1, 4):
        ups_key = "ups%ds" % ns
        ret[ups_key] = {}
        for np in pdg.VALID_UPS_DECAYS[ns]:
            binning = tools.axis2bins(
                tools.get_axis(np, cfg_mc[ups_key]['axis'])
            )
            chip_key = "chib%dp" % np
            ret[ups_key][chip_key] = {}
            for bin in binning:
                amin, amax = float('inf'), float('-inf')
                for nb in range(1, 3):
                    chib_key = "chib%d%dp" % (nb, np)

                    db_chib = db_pol[ups_key][bin][chib_key]
                    for w in range(3):
                        wkey = "w%d" % w
                        if wkey in db_chib:
                            val, err = db_chib[wkey]
                            amin = min(amin, val - err)
                            amax = max(amax, val + err)
                ret[ups_key][chip_key][bin] = (int(
                    (1 - amin) * 100), int((amax - 1) * 100))
    return ret


def publish(ret, cfg_pol):

    for ns in range(1, 4):
        ups_key = "ups%ds" % ns
        ups = ret[ups_key]
        for np in pdg.VALID_UPS_DECAYS[ns]:
            chip_key = "chib%dp" % np
            chip = ups[chip_key]
            binning = sorted(chip.keys())

            title = cfg_pol['title'].format(ns=ns, np=np)
            label = "syst:pol:{chip_key}_{ups_key}".format(chip_key=chip_key,
                                                           ups_key=ups_key)
            tab = table.PtTable(title=title, label=label, ns=ns,
                                binning=binning)
            tab.add_row("max", cfg_pol['row_title'])
            for bin in binning:
                cell = tab.get_bin(bin)
                cell.add_value("max", max(chip[bin][0], chip[bin][1]))

            print table.table2tex(tab)

if __name__ == '__main__':
    cfg_pol = tools.load_config('rep_pol')
    ret = collect(cfg_pol)
    publish(ret, cfg_pol)
