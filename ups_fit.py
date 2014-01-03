from ups_model import UpsModel


def prepare_model(canvas, name, year, data, interval, nbins, pt_ups, has_splot,
                  profile):
    m1, m2 = interval
    model = UpsModel(canvas=canvas,
                     data=data,
                     interval=interval,
                     nbins=nbins,
                     is_pull=False
                     )

    if profile.get("fixed_m1s", False):
        model.m1s.fix(profile["fixed_m1s"])

    return model
