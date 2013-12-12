#!/usr/bin/env python

import tools
import table

def create_table(label, title, scale, cfg_rows, ns):
    tab = table.Table(label=label, title=title, scale=scale)
    for np in range(1, 4):
        for nb in range(1, 3):
            for row in cfg_rows:
                key = row["key"].format(nb=nb, np=np)
                title = row["title"].format(nb=nb, np=np)
                tab.add_row(key=key, title=title)
        tab.space()
    return tab

def main():

    cfg_pol = tools.load_config("rep_pol")
    cfg_mc = tools.load_config("mc")["decays"]

    db_pol = tools.get_db("polarization")

    for ns in range(1, 4):
        title = cfg_rep["title"].format(
            ns=ns,
            np=np
        )
        label = cfg_rep["label"].format(
            ns=ns,
            np=np
        )        
        ups_key = "ups%ds" % ns
        xaxis = cfg_mc[ups_key]
        bins = tools.axis2bins(xaxis)
        maxbins = cfg_rep["maxbins"]

        subtables = table.SubTables()
        for i in range(len(bins) / maxbins + 1):
            tab = create_table(label=)


if __name__ == '__main__':
    main()
