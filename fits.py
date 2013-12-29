#!/usr/bin/env python
# Usage: th fit
# Summary: Fit models
# Help: th fit -h

# import sys
import argparse
from sh import gnome_terminal


import tools
# from th.log import Logger

from IPython import embed as shell  # noqa


def get_cli_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--complete', help='Show completion list', action='store_true')
    parser.add_argument(
        '--year', help='Show completion list',
        choices=['all', '2011', '2012'])
    parser.add_argument(
        '--profile', help='Binning information')
    return parser.parse_args()


def complete():
    print "--year"
    print "--profile"


def main():
    # log = Logger()
    cli_args = get_cli_args()
    if cli_args.complete:
        complete()
        exit(0)

    cfg = tools.load_config("fits")[cli_args.profile]

    if cli_args.year == 'all':
        years = ['2011', '2012']
    else:
        years = [cli_args.year]

    args = []
    sleep = 0

    if "lambda" in cfg["profiles"]:
        cfg["profiles"].remove("lambda")
        cfg["profiles"] += ["lambda%d" % i for i in range(0, 11)]

    for profile in cfg["profiles"]:
        for year in years:
            for bin in cfg["binning"]:

                args += ["--tab-with-profile", "Tomorrow"]
                args += ["--title",
                         "{0}-{1} {2} {3}".format(
                             bin[0], bin[1], year, profile
                         )]
                args += ["-e", "./fit.sh" +
                         " {0} {1} {2} {3} {4} {5}".format(sleep, cfg["decay"],
                                                           year, bin[
                                                               0], bin[1],
                                                           profile
                                                           )
                         ]
                sleep += 2

    gnome_terminal(args)
    # print(gnome_terminal.bake(args))

    # shell()

if __name__ == '__main__':
    main()
