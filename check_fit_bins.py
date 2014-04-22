#!/usr/bin/env python
"""Check bin presence in the fit database.

Usage:
  check_fit_bins.py --db=<dbpath> --bins=<bins>

Options:
  --db=<db>       Path to database
  --bins=<bins>   Axis or bins in form [1,2,3,4] or [[1,2], [2,4]]
  -h --help             Show this screen.
"""
import env  # noqa
import tools 
from collections import defaultdict
import simplejson as json
from docopt import docopt
import shelve

def check_fit_bins(db, bins):
    if not (isinstance(bins[0], list) or isinstance(bins[0], tuple)):
        bins = tools.axis2bins(bins)

    missing = defaultdict(list)
    for year in ["2011", "2012"]:
        if year not in db:
            missing[year].append("Could not find year %s" % year)
            continue
        for bin in [tuple(x) for x in bins]:
            if bin not in db[year].keys():
                missing[year].append(bin)
        if missing:
            return (False, missing)

        return (True, None)

def main():
    cli_args = docopt(__doc__, version='v1.0')
    db = tools.get_db(cli_args["--db"], "r")
    bins = json.loads(cli_args["--bins"])
    
    status, missing = check_fit_bins(db, bins)
    if not status:
        print("Missing data %s" % str(missing))


if __name__ == '__main__':
    main()
