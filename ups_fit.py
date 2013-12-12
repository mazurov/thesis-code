from ups_model import UpsModel


def prepare_model(canvas, name, data, mc, interval, nbins, pt_ups, has_splot,
                  profile):
    m1, m2 = interval
    model = UpsModel(canvas=canvas,
                     data=data,
                     interval=interval,
                     nbins=nbins
                     )

    if "fixed_m1s" in profile:
        model.m1s.fix(profile["fixed_m1s"])

    return model
