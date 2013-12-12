from chib1s_model import ChibModel
from mctools import MC


def get_lambda_b1b2(pt_ups1):
    # frac = (0.6, 0.5, 0.5)

    a1 = 0.5 if pt_ups1 < 10 else 0.6
    if pt_ups1 < 8:
        a2 = a3 = 0.4
    elif pt_ups1 < 22:
        a2 = a3 = 0.5
    else:
        a2 = a3 = 0.6

    return a1, a2, a3


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

        return (round((sigma2 / sigma1).value(), 1),
                round((sigma3 / sigma1).value(), 1)
                )


def prepare_model(canvas, name, data, mc, interval, nbins, pt_ups,
                  has_splot, profile):
    order = 2
    pt_ups1, pt_ups2 = pt_ups
    for min_pt, order_ in profile["bgorder"]:
        if pt_ups1 < min_pt:
            order = order_
            break

    lambda_b1b2 = get_lambda_b1b2(
        pt_ups1) if "lambda_b1b2" not in profile else profile["lambda_b1b2"]
    mct_arr = [MC(db=mc, ns=1, np=np) for np in range(1, 4)]
    
    if profile["fixed_sigma"]:
        sigma = get_sigma(mct_arr[0], pt_bin=pt_ups, scale=1)
        sfracs = get_sfracs(mct_arr=mct_arr, pt_bin=pt_ups)
    else:
        sigma, sfracs = None, (None, None)

    has_3p = pt_ups1 >= profile["chib3p_min_pt_ups"]
    model = ChibModel(canvas=canvas,
                      data=data,
                      sigma=sigma,
                      sfracs=sfracs,
                      binning=(nbins, interval[0], interval[1]),
                      bgorder=order,
                      frac=lambda_b1b2,
                      has_3p=has_3p
                      )
    return model
    # if "fixed_m1s" in profile:
    #     model.m1s.fix(profile["fixed_m1s"])

#     return model

#         model = ChibModel(canvas=canvas,
#                           data=data,
#                           interval=interval
#                           nbins=nbins,
#                           bgorder=order,
#                           frac=frac,
#                           sfracs=sfracs,
#                           mean_3p=mean_3p,
#                           has_3p=has_3p)


# if "fixed_mean" in cfg:
#     model.chib1p.mean1.fix(cfg["fixed_mean"])
