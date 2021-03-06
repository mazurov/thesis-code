from chib1s_model import ChibModel
from mctools import MC
import tools
import pdg

import AnalysisPython.PyRoUts as pyroot


def get_lambda_b1b2(pt_ups1):
    return (0.5, 0.5, 0.5)
    # frac = (0.6, 0.5, 0.5)

    # a1 = 0.5 if pt_ups1 < 10 else 0.6
    # if pt_ups1 < 8:
    #     a2 = a3 = 0.4
    # elif pt_ups1 < 22:
    #     a2 = a3 = 0.5
    # else:
    #     a2 = a3 = 0.6

    # return a1, a2, a3


def get_sigma(mc, pt_bin, scale=1):
    return (round(mc.sigma(pt_bin).value(), 3) * scale
            if mc.sigma(pt_bin)
            else None
            )


def get_sfracs(mct_arr, pt_bin):
    sigma1 = mct_arr[0].sigma(pt_bin)
    if not sigma1:
        return (None, None)
    else:
        sigma2 = mct_arr[1].sigma(pt_bin)
        sigma3 = mct_arr[2].sigma(pt_bin)

        return (round((sigma2 / sigma1).value(), 2),
                round((sigma3 / sigma1).value(), 2)
                )


def prepare_model(canvas, name, year, data, interval, nbins, pt_ups,
                  has_splot, profile):

    # Use 2012 MC if we fit joined datasset
    # mc_year = year if year != "all" else "2012"
    mc_year = "2011" # scale to this value
    mc = tools.get_db(profile["mc"], "r")["mc%s" % mc_year]['ups1s']

    order = 2
    pt_ups1, pt_ups2 = pt_ups
    for min_pt, order_ in profile["bgorder"]:
        if pt_ups1 < min_pt:
            order = order_
            break
    lambda_b1b2 = [profile["lambda_b1b2"]] * 3
    mct_arr = [MC(db=mc, ns=1, np=np) for np in range(1, 4)]

    sigma = None
    sfracs = (profile["mc_sigma_2p_1p"], profile["mc_sigma_3p_1p"])    
    if profile["fixed_sigma"]:
        sigma_scale = profile.get("mc_sigma_scale", 1)
        sigma = get_sigma(mct_arr[0], pt_bin=pt_ups, scale=sigma_scale)
        if year == "2012":
            sigma += profile["mc_sigma_2012_2011"]
    elif not profile["fixed_sigma_ratio"]:
        sfracs = (None, None)

    has_3p = pt_ups1 >= profile["chib3p_min_pt_ups"]
    mean_3p = profile.get("fixed_mean_3p", pdg.CHIB13P)

    model = ChibModel(canvas=canvas,
                      data=data,
                      sigma=sigma,
                      sfracs=sfracs,
                      binning=(nbins, interval[0], interval[1]),
                      bgorder=order,
                      frac=lambda_b1b2,
                      mean_3p=mean_3p,
                      has_3p=has_3p
                      )

    if profile.get("fixed_mean", False):
        model.chib1p.mean1.fix(profile["fixed_mean"])

    fixed_db_name = profile.get("fixed_mean_db", False)
    if fixed_db_name:
        fixed_mean = profile.get("fixed_mean")
        fixed_db = tools.get_db(fixed_db_name)
        mean = pyroot.VE(str(fixed_db[year][tuple(pt_ups)]["mean_b1_1p"]))
        up, down = mean.value() + mean.error(), mean.value() - mean.error()
        if abs(fixed_mean - up) > abs(fixed_mean - down):
            new_fixed_mean = up
        else:
            new_fixed_mean = down
        model.chib1p.mean1.fix(new_fixed_mean)

    return model
