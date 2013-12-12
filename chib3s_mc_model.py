import ROOT

from AnalysisPython.PyRoUts import cpp
ExpoPositive = cpp.Analysis.Models.ExpoPositive
PolyPositive = cpp.Analysis.Models.PolyPositive
CrystalBallDS = cpp.Analysis.Models.CrystalBallDS

import pdg
from model import BaseModel

from IPython import embed as shell  # noqa


class Chib3P(object):

    def __init__(self, dm):
        m_pdg = (pdg.CHIB13P.value() + pdg.CHIB23P.value()) / 2
        self.mean = ROOT.RooRealVar("mean", "mean", m_pdg,
                                    m_pdg - 0.05, m_pdg + 0.05)

        self.sigma = ROOT.RooRealVar("sigma", "sigma",
                                     0.02, 0.02 - 0.015, 0.02 + 0.015)

        self.n = ROOT.RooRealVar("n", "n", 5, 0, 20)
        self.n.setConstant(True)
        self.alpha = ROOT.RooRealVar("a", "a", -1.25, -5, 0)
        self.alpha.setConstant(True)
        self.pdf = ROOT.RooCBShape("cb", "cb", dm, self.mean,
                                   self.sigma, self.alpha, self. n)

        # self.pdf = ROOT.RooGaussian("cb", "cb", dm, self.mean,
        #                            self.sigma)


class Background(object):

    def __init__(self, dm, dm_begin, dm_end):
        self.phi1 = ROOT.RooRealVar("phi1", "phi1", 0, -3.1415, +3.1415)

        self.tau = ROOT.RooRealVar("tau", "tau", -1.5, -100, 0)

        self.pdf = ExpoPositive("bg", "bg", dm, self.tau, self.phi1,
                                dm_begin, dm_end)


class ChibMCModel(BaseModel):

    def __init__(self, canvas, p, binning,
                 data=None, is_pull=True, dm=None, b=None, user_labels=None):
        super(ChibMCModel, self).__init__(canvas=canvas,
                                          data=data,
                                          interval=binning[1:],
                                          xfield="dmplusm3s",
                                          nbins=binning[0],
                                          user_labels=user_labels,
                                          is_pull=is_pull)
        self.p = p

        klass = globals()["Chib%dP" % self.p]
        self.chib = klass(dm=self.x)
        self.bg = Background(dm=self.x, dm_begin=self.x0, dm_end=self.x1)

        self.np = ROOT.RooRealVar("N", "Signal(N)", 0, 0, 1e+7)
        self.b = ROOT.RooRealVar("B", "Background", 0, 0, 1e+7)

        self.alist_pdf = ROOT.RooArgList(
            self.chib.pdf,
            self.bg.pdf
        )

        self.alist_yields = ROOT.RooArgList(
            self.np,
            self.b
        )

        self.pdf = ROOT.RooAddPdf("model", "model", self.alist_pdf,
                                  self.alist_yields)

    def labels(self):
        frame = self.frame
        frame.SetTitle("")
        frame.GetXaxis().SetTitle("")
        frame.GetYaxis().SetTitle("")
        # frame.GetXaxis().SetTitle("m(#mu^{+}#mu^{-}#gamma) - "
        # "m(#mu^{+ }#mu^{-}) [GeV/c^{2}]")
        # self.candidates()

    def draw_after(self):
        frame = self.frame
        frame.drawAfter("model_Norm[%s]_Comp[cb]" % self.xfield, "h_ds")

    def curves(self):
        frame = self.frame
        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.bg.pdf.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kBlue))
        # self.pdf.plotOn(frame,
        #                 ROOT.RooFit.Components(self.chib.pdf.GetName()),
        #                 ROOT.RooFit.LineStyle(ROOT.kSolid),
        #                 ROOT.RooFit.LineColor(ROOT.kBlue))
