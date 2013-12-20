import ROOT
from AnalysisPython.PySelector import SelectorWithCuts

import tools
from collections import namedtuple
from IPython import embed as shell  # noqa

# ========================================================================
RAD = ROOT.RooAbsData
if RAD.Tree != RAD.getDefaultStorageType():
    print 'DEFINE default storage type to be TTree! '
    RAD.setDefaultStorageType(RAD.Tree)
# =============================================================================


class Selector(SelectorWithCuts):

    def __init__(self, selection, columns):
        self.selection = tools.cut_dict2str(selection)
        SelectorWithCuts.__init__(self, self.selection)

        DataType = namedtuple('DataSet', columns)
        self.columns = DataType(
            *[ROOT.RooRealVar(name, name, 0) for name in columns])

        aset = ROOT.RooArgSet("args")

        for c in self.columns:
            aset.add(c)

        self.varset = ROOT.RooArgSet(aset)
        self.data = ROOT.RooDataSet("ds", "ds", self.varset)

        self.events = 0
        self.progress = None

    def dataset(self):
        return self.data

    # the only one important method
    def Process(self, entry):
        if self.GetEntry(entry) <= 0:
            return 0
        tuple = self.fChain
        for c in self.columns:
            c.setVal(getattr(tuple, c.GetName()))

        self.data.add(self.varset)
        return 1

# class WeightSelectror(SelectorWithCuts):
#     def angles(cols):
#         v_chib = TVector3(cols["px_cb"], cols["py_cb"], cols["pz_cb"])

#         # for boosting to chib lab
#         v_bchib = TVector3(
#             -cols["px_cb"] / cols["e_chib"],
#             -cols["py_cb"] / cols["e_chib"],
#             cols["pz_cb"] / cols["e_chib"]
#         )
#         # v_ups = TVector3(px_y, py_y, pz_y)

#         # boosting
#         lv_ups = TLorentzVector(
#             cols["px_y"],
#             cols["py_y"],
#             cols["pz_y"],
#             cols["e_y"]
#         )
#         lv_mup = TLorentzVector(
#             cols["px_mup"],
#             cols["py_mup"],
#             cols["pz_mup"],
#             cols["e_mup"]
#         )
#         lv_mum = TLorentzVector(
#             cols["px_mum"],
#             cols["py_mum"],
#             cols["pz_mum"],
#             cols["e_mum"]
#         )

#         lv_ups.Boost(v_bchib)
#         lv_mup.Boost(v_bchib)
#         lv_mum.Boost(v_bchib)

#         v_ups_chib = TVector3(
#             lv_ups.Px(), lv_ups.Py(), lv_ups.Pz())
#         v_mup_chib = TVector3(
#             lv_mup.Px(), lv_mup.Py(), lv_mup.Pz())
#         v_mum_chib = TVector3(
#             lv_mum.Px(), lv_mum.Py(), lv_mum.Pz())

#         # First result
#         theta = v_ups_chib.Angle(v_chib)
#         # print cos(theta_chib), lv

#         n_chib = v_chib.Unit()
#         n_ups = v_ups_chib.Unit()
#         n_mup = v_mup_chib.Unit()
#         n_mum = v_mum_chib.Unit()

#         n_perp_ups = n_mup.Cross(n_mum)
#         n_perp_chib = n_ups.Cross(n_chib)

#         cosphi = n_perp_chib.Dot(n_perp_ups)

#         v_bups = TVector3(-lv_ups.Px() / lv_ups.E(),
#                           -lv_ups.Py() / lv_ups.E(),
#                           -lv_ups.Pz() / lv_ups.E())
#         lv_mup.Boost(v_bups)
#         lv_mum.Boost(v_bups)

#         thetap = lv_mup.Angle(v_ups_chib)

#         return theta, thetap, cosphi

#     def __init__(self, selection, columns):
#         self.selection = selection
#         SelectorWithCuts.__init__(self, self.selection)
