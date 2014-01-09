
from AnalysisPython.PyRoUts import VE
import math
from mctools import MC

from IPython import embed as shell  # noqa


def get_db_param(db, param, year, bin):
    db_bin = db[str(year)][tuple(bin)]
    n = db_bin.get(param, None)
    if not n:
        return None
    if isinstance(n, tuple):
        return VE(str(n))
    return n


def get_param_scale(db_ref, db_syst, param, year, bin):
    n1 = get_db_param(db_ref, param, year, bin)
    n2 = get_db_param(db_syst, param, year, bin)
    if not (n1 or n2):
        return None
    return n2.value() / n1.value()


def get_chib_yield(db, np, year, bin):
    return get_db_param(db, "N%dP" % np, year, bin)


def get_ups_yield(db, ns, year, bin):
    return get_db_param(db, "N%dS" % ns, year, bin)


def get_chib_yield_scale(db_ref, db_syst, np, year, bin):
    return get_param_scale(db_ref, db_syst, "N%dP" % np, year, bin)


def get_param_err(db, param, year, bin):
    n = get_db_param(db, param, year, bin)
    if not n:
        return None
    return n.error() / n.value()


def get_chib_yield_err(db, np, year, bin):
    return get_param_err(db, "N%dP" % np, year, bin)


def get_squared_error(db_ref, dbs_syst, param, year, bin):
    sqret = [0, 0]
    for db_syst in dbs_syst:
        scale = get_param_scale(db_ref, db_syst, param, year, bin)
        if scale is None:
            continue
        index = 1 if scale > 1 else 0

        sqret[index] += (1 - scale) ** 2

    return (math.sqrt(sqret[0]), math.sqrt(sqret[1]))


def get_chib_squared_error(db_ref, dbs_syst, np, year, bin):
    return get_squared_error(db_ref, dbs_syst, "N%dP" % np, year, bin)


def get_fraction(db_chib, db_ups, db_mc, year, bin, ns, np,
                 scalecb=1, scaleups=1, scaleeff=1):
    nchib = get_chib_yield(db_chib, np, year, bin)
    nups = get_ups_yield(db_ups, ns, year, bin)

    # TODO: simplify mctools
    mct = MC(db=db_mc["mc%s" % str(year)]["ups%ds" % ns], ns=ns, np=np)
    eff = mct.eff(bin=bin)

    if not (nchib and nups and eff):
        return None
    nchib_scaled = VE(nchib.value() * scalecb, nchib.error()**2)
    nups_scaled = VE(nups.value() * scaleups, nups.error()**2)
    eff_scaled = VE(eff.value() * scaleeff, eff.error()**2)
    
    res = (nchib_scaled)/eff_scaled/(nups_scaled)
    return res
