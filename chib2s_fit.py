from chib2s_model import ChibModel
from mctools import MC
import tools
import pdg

import AnalysisPython.PyRoUts as pyroot


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

    lambda_b1b2 = [profile["lambda_b1b2"]] * 2

    mct_arr = [MC(db=mc, ns=2, np=np) for np in range(2, 4)]

    sigma, sfrac3 = None, None
    if profile.get("fixed_sigma", False):
        sigma = get_sigma(mct_arr[0], pt_bin=pt_ups, scale=1)
        if not sigma:
            print "No sigma  information in MC"

    if profile.get("fixed_sigma_ratio", False):
        sfrac3 = get_sfrac(mct_arr=mct_arr, pt_bin=pt_ups)

    # has_3p = [pt_ups1, pt_ups2] in profile["3p_bins"]
    has_3p = True
    bgorder = profile["bgorder"]
    mean_3p = profile.get("fixed_mean_3p", pdg.CHIB13P)

    model = ChibModel(canvas=canvas,
                      data=data,
                      sigma=sigma,
                      sfrac3=sfrac3,
                      binning=(nbins, interval[0], interval[1]),
                      bgorder=bgorder,
                      frac=lambda_b1b2,
                      mean_3p=mean_3p,
                      has_3p=has_3p
                      )
    if profile.get("fixed_mean", False):
        model.chib2p.mean1.fix(profile["fixed_mean"])
    
    fixed_db_name = profile.get("fixed_mean_db", False)
    if fixed_db_name:
        fixed_mean = profile.get("fixed_mean")
        fixed_db = tools.get_db(fixed_db_name)
        mean = pyroot.VE(str(fixed_db[year][tuple(pt_ups)]["mean_b1_2p"]))
        up, down = mean.value() + mean.error(), mean.value() - mean.error()
        if abs(fixed_mean - up) > abs(fixed_mean - down):
            new_fixed_mean = up
        else:
            new_fixed_mean = down
        model.chib2p.mean1.fix(new_fixed_mean)

    return model
