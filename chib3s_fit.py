from chib3s_model import ChibModel
from mctools import MC
import tools


def get_lambda_b1b2(pt_ups):
    return 0.5


def get_sigma(mct, pt_bin, scale=1):
    return (round(mct.sigma(pt_bin).value(), 3) * scale
            if mct.sigma(pt_bin) else None)


def prepare_model(canvas, name, year, data, interval, nbins, pt_ups,
                  has_splot, profile):

    # Use 2012 MC if we fit joined datasset
    mc_year = year if year != "all" else "2012"
    mc = tools.get_db(profile["mc"], "r")["mc%s" % mc_year]["ups3s"]

    pt_ups1, pt_ups2 = pt_ups

    bgorder = profile["bgorder"]

    lambda_b1b2 = (get_lambda_b1b2(pt_ups1)
                   if "lambda_b1b2" not in profile
                   else profile["lambda_b1b2"])
    mct = MC(db=mc, ns=3, np=3)

    sigma = None
    if profile["fixed_sigma"]:
        sigma = get_sigma(mct, pt_bin=pt_ups, scale=1)
        if not sigma:
            print "No sigma  information in MC"

    model = ChibModel(canvas=canvas,
                      data=data,
                      sigma=sigma,
                      binning=(nbins, interval[0], interval[1]),
                      bgorder=bgorder,
                      frac=lambda_b1b2
                      )
    return model