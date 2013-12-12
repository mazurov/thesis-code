import ROOT
# from AnalysisPython.PyRoUts import hID, cpp, VE

from model import BaseModel
import pdg
from IPython import embed as shell  # noqa


class UpsBackground(object):

    """
    Define pdf for background : Exponential
    """
    # constructor

    def __init__(self, name, mass):
        self.tau = ROOT.RooRealVar("tau_bg", "tau_bg",
                                   -1, -25, 10)
        self.phi1 = ROOT.RooRealVar("phi1_bg", "phi1_bg", 0, -3.1415, 3.1415)
        self.phi2 = ROOT.RooRealVar("phi2_bg", "phi2_bg", 0, -3.1415, 3.1415)
        self.phi3 = ROOT.RooRealVar("phi3_bg", "phi3_bg", 0, -3.1415, 3.1415)
        self.alist = ROOT.RooArgList(self.phi1)

        # self.pdf = ROOT.RooExponential("exp_%s" % name, "exp(%s)" % name,
        #                                mass, self.tau)

        # self.pdf = cpp.Analysis.Models.ExpoPositive(
        #     "exp_bg", "exp_bg",
        #     mass, self.tau, self.alist, 8.5, 12)

        self.pdf = ROOT.RooExponential(
            "exp_bg", "exp_bg",
            mass, self.tau)

        # self.pdf = cpp.Analysis.Models.PolyPositive(
        #     "poly_bg", "poly_bg",
        #     mass, self.alist, 8.5, 12)


class UpsModel (BaseModel):

    def __init__(self, canvas, data, interval, nbins=175, user_labels=None,
                 is_pull=True):

        super(UpsModel, self).__init__(canvas=canvas,
                                       data=data,
                                       interval=interval,
                                       xfield="m_dtf", nbins=nbins,
                                       user_labels=user_labels,
                                       is_pull=is_pull)
        name = "Y"
        m_y1s = pdg.UPS1S.value()
        s_y1s = 4.3679e-02
        dm_y2s = pdg.UPS2S.value() - m_y1s
        dm_y3s = pdg.UPS3S.value() - m_y1s

        self.m1s = ROOT.RooRealVar("m1s", "mean(%s)" % name, m_y1s,
                                   m_y1s - 0.3 * s_y1s, m_y1s + 0.3 * s_y1s)

        self.sigma = ROOT.RooRealVar("sigma", "sigma(%s)" % name, s_y1s,
                                     0.5 * s_y1s, 2.0 * s_y1s)

        self.n = ROOT.RooRealVar("n", "n", 1, 1, 5)  # 4

        self.alphaL = ROOT.RooRealVar("alphaL", "alphaL", 2,  # 1.28,
                                      1.0, 3.5)

        self.alphaR = ROOT.RooRealVar("alphaR", "alphaR", -2,
                                      -3.5, -1)

        self.n.setConstant(True)
        self.alphaL.setConstant(True)
        self.alphaR.setConstant(True)

        self.y1s_1 = ROOT.RooCBShape("y1s_1_%s" % name,
                                     "CrystalBall(%s)(1)" % name,
                                     self.x,
                                     self.m1s,
                                     self.sigma,
                                     self.alphaL,
                                     self.n)

        self.y1s_2 = ROOT.RooCBShape("y1s_2_%s" % name,
                                     "CrystalBall(%s)(2)" % name,
                                     self.x,
                                     self.m1s,
                                     self.sigma,
                                     self.alphaR,
                                     self.n)

        self.dm2s = ROOT.RooRealVar("dm2s",
                                    "dm2s(%s)" % name,
                                    dm_y2s,
                                    dm_y2s - 0.008,
                                    dm_y2s + 0.008)
        self.dm2s.setConstant(True)
        self.aset11 = ROOT.RooArgList(self.m1s, self.dm2s)
        self.m2s = ROOT.RooFormulaVar("m2s",
                                      "m2s(%s)" % name,
                                      "m1s+dm2s",
                                      self.aset11)

        self.aset12 = ROOT.RooArgList(self.sigma, self.m1s, self.m2s)
        self.s2s = ROOT.RooFormulaVar("s2s(%s)" % name,
                                      "s2s(%s)" % name,
                                      "sigma*m2s/m1s",
                                      self.aset12)
        self.y2s = ROOT.RooCBShape("y2s_%s" % name,
                                   "CristalBall(%s)" % name,
                                   self.x,
                                   self.m2s,
                                   self.s2s,
                                   self.alphaL,
                                   self.n)

        self.dm3s = ROOT.RooRealVar("dm3s",
                                    "dm3s(%s)" % name,
                                    dm_y3s,
                                    dm_y3s - 0.009,
                                    dm_y3s + 0.009)
        self.dm3s.setConstant(True)
        self.aset21 = ROOT.RooArgList(self.m1s, self.dm3s)
        self.m3s = ROOT.RooFormulaVar("m3s",
                                      "m3s(%s)" % name,
                                      "m1s+dm3s",
                                      self.aset21)

        self.aset22 = ROOT.RooArgList(self.sigma, self.m1s, self.m3s)
        self.s3s = ROOT.RooFormulaVar("s3s(%s)" % name,
                                      "s3s(%s)" % name,
                                      "sigma*m3s/m1s",
                                      self.aset22)

        self.y3s = ROOT.RooCBShape("y3s_%s" % name,
                                   "CristalBall(%s)" % name,
                                   self.x,
                                   self.m3s,
                                   self.s3s,
                                   self.alphaL,
                                   self.n)

        self.bg = UpsBackground('Background', self.x)

        self.n1s = ROOT.RooRealVar("N1S", "Signal(Y1S)", 100, 0, 1.e+8)
        self.n1s_1 = ROOT.RooRealVar(
            "N1S_1", "Signal(Y1S)(1)", 100, 0, 1.e+10)

        self.asetn1s = ROOT.RooArgList(self.n1s, self.n1s_1)
        self.n1s_2 = ROOT.RooFormulaVar(
            "N1S_2", "N1S_2", "N1S-N1S_1", self.asetn1s)

        self.n2s = ROOT.RooRealVar("N2S", "Signal(Y2S)", 100, 0, 1.e+8)
        self.n3s = ROOT.RooRealVar("N3S", "Signal(Y3S)", 100, 0, 1.e+8)
        self.b = ROOT.RooRealVar("B", "Background", 10, 0, 1.e+8)

        self.alist1 = ROOT.RooArgList(
            self.y1s_1,
            self.y2s,
            self.y3s,
            self.bg.pdf
        )
        self.alist2 = ROOT.RooArgList(
            self.n1s,
            # self.n1s_1,
            # self.n1s_2,
            self.n2s,
            self.n3s,
            self.b
        )

        self.pdf = ROOT.RooAddPdf("model",
                                  "model",
                                  self.alist1,
                                  self.alist2)
        self._splots = []

    def curves(self):
        frame = self.frame
        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.bg.pdf.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kBlue))

    def labels(self):
        frame = self.frame
        frame.SetTitle("")
        frame.GetXaxis().SetTitle("")
        frame.GetYaxis().SetTitle("")
        # frame.GetXaxis().SetTitle("m(#mu^{+}#mu^{-}) #left[GeV/c^{2}#right]")
        # self.candidates()
        # frame.GetYaxis().SetTitle("Candidates")
