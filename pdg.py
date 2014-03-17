from AnalysisPython.PyRoUts import VE


CHIB11P = VE(9.89278, 0.0004 ** 2)
CHIB21P = VE(9.91221, 0.0004 ** 2)
CHIB12P = VE(10.25546, 0.00055 ** 2)
CHIB22P = VE(10.26865, 0.00055 ** 2)
CHIB13P = VE(10.508, 0.00065 ** 2)
CHIB23P = VE(10.520, 0.00065 ** 2)


UPS1S = VE(9.46030, 0.00026 ** 2)
UPS2S = VE(10.02326, 0.00031 ** 2)
UPS3S = VE(10.3552, 0.0005 ** 2)


CHIB = []
for p in range(3):
    for b in range(2):
        chib = globals()["CHIB{b}{p}P".format(b=b + 1, p=p + 1)]
        CHIB.append(chib)

# DM1S = []
# DM2S = []
# DM3S = []


# for s in range(3):
#     ups_name = str("UPS{s}S".format(s=s+1))
#     ups = globals()[ups_name]
#     dms = globals()["DM{s}S".format(s=s+1)]
#     for p in range(3):
#         for b in range(2):
#             name = str("CHIB{b}{p}P".format(b=b+1, p=p+1))
#             chib = globals()[name]
#             diff = chib - ups
#             if diff.value() >0:
# print t.yellow("PDG %s" % name), chib, t.yellow("M-%s" % ups_name), diff

#             dms.append(diff)


BR11_Y1S = VE(0.339, 0.022 ** 2)
BR21_Y1S = VE(0.191, 0.012 ** 2)
BR12_Y1S = VE(0.092, 0.008 ** 2)
BR22_Y1S = VE(0.07, 0.007 ** 2)
BR12_Y2S = VE(0.199, 0.019 ** 2)
BR22_Y2S = VE(0.106, 0.026 ** 2)

BR_CB_UPS = {
    "b11P1S": BR11_Y1S,
    "b21P1S": BR21_Y1S,
    "b12P1S": BR12_Y1S,
    "b22P1S": BR22_Y1S,
    "b12P2S": BR12_Y2S,
    "b22P2S": BR22_Y2S
}


VALID_UPS_DECAYS = {
    1: [1, 2, 3],
    2: [2, 3],
    3: [3]
}
