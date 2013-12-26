from chib2s_model import ChibModel
from mctools import MC
import tools


def get_lambda_b1b2(pt_ups):
    return 0.5, 0.5


def get_sigma(mc, pt_bin, scale=1):
    return (round(mc.sigma(pt_bin).value(), 3) * scale
            if mc.sigma(pt_bin) else None)


def get_sfrac(mct_arr, pt_bin):
    sigma2 = mct_arr[0].sigma(pt_bin)
    if not sigma2:
        return None
    else:
        sigma3 = mct_arr[1].sigma(pt_bin)
        return round((sigma3 / sigma2).value(), 2)


def prepare_model(canvas, name, year, data, interval, nbins, pt_ups,
                  has_splot, profile):

    # Use 2012 MC if we fit joined datasset
    mc_year = year if year != "all" else "2012"
    mc = tools.get_db(profile["mc"], "r")["mc%s" % mc_year]["ups2s"]

    pt_ups1, pt_ups2 = pt_ups

    bgorder = profile["bgorder"]

    lambda_b1b2 = (get_lambda_b1b2(pt_ups1)
                   if "lambda_b1b2" not in profile
                   else profile["lambda_b1b2"])
    mct_arr = [MC(db=mc, ns=2, np=np) for np in range(2, 4)]

    sigma, sfrac3 = None, None
    if profile["fixed_sigma"]:
        sigma = get_sigma(mct_arr[0], pt_bin=pt_ups, scale=1)
        if sigma:
            sfrac3 = get_sfrac(mct_arr=mct_arr, pt_bin=pt_ups)
        else:
            print "No sigma  information in MC"

    model = ChibModel(canvas=canvas,
                      data=data,
                      sigma=sigma,
                      sfrac3=sfrac3,
                      binning=(nbins, interval[0], interval[1]),
                      bgorder=bgorder,
                      frac=lambda_b1b2
                      )
    return model
