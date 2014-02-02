import ROOT

from AnalysisPython.PyRoUts import cpp
# ExpoPositive = cpp.Analysis.Models.ExpoPositive
# PolyPositive = cpp.Analysis.Models.PolyPositive
CrystalBallDS = cpp.Analysis.Models.CrystalBallDS

import pdg
from model import BaseModel

from IPython import embed as shell  # noqa


class Ups(object):

    def __init__(self, mass):
        m_pdg = pdg.UPS1S.value()

        self.mean = ROOT.RooRealVar("mean", "mean", m_pdg,
                                    m_pdg - 0.3, m_pdg + 0.3)

        self.sigma = ROOT.RooRealVar("sigma", "sigma",
                                     0.045, 0.045 - 0.02, 0.045 + 0.02)

        self.nL = ROOT.RooRealVar("nL", "nL", 1, 1, 5)  # 4
        self.nR = ROOT.RooRealVar("nR", "nR", 10, 1, 10)  # 4

        self.alphaL = ROOT.RooRealVar("alphaL", "alphaL", 1.6,  # 1.28,
                                      0, 3.5)
        self.alphaR = ROOT.RooRealVar("alphaR", "alphaR", 1.6,
                                      0, 3.5)

        # self.nL.setConstant(True)
        # self.nR.setConstant(True)
        # self.alphaL.setConstant(True)
        # self.alphaR.setConstant(True)

        self.pdf = CrystalBallDS("y",
                                 "CrystalBall",
                                 mass,
                                 self.mean,
                                 self.sigma,
                                 self.alphaL,
                                 self.nL,
                                 self.alphaR,
                                 self.nR)
        
        # self.pdf = ROOT.RooCBShape("y",
        #                            "CrystalBall",
        #                            mass,
        #                            self.mean,
        #                            self.sigma,
        #                            self.alphaL,
        #                            self.nL)

        # self.pdf = ROOT.RooGaussian("cb", "cb", dm, self.mean,
        #                            self.sigma)


class UpsMCModel(BaseModel):

    def __init__(self, canvas, binning, data=None, is_pull=True,
                 user_labels=None):
        super(UpsMCModel, self).__init__(canvas=canvas,
                                         data=data,
                                         interval=binning[1:],
                                         xfield="m_dtf",
                                         nbins=binning[0],
                                         user_labels=user_labels,
                                         is_pull=is_pull)
        self.ups = Ups(mass=self.x)

        self.n = ROOT.RooRealVar("N", "Signal(N)", 0, 0, 1e+7)
        self.b = ROOT.RooRealVar("B", "Background", 0, 0, 1e+7)

        self.alist_pdf = ROOT.RooArgList(
            self.ups.pdf,
        )

        self.alist_yields = ROOT.RooArgList(
            self.n
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
        # frame = self.frame
        # frame.drawAfter("model_Norm[%s]_Comp[cb]" % self.xfield, "h_ds")
        pass

    def curves(self):
        frame = self.frame
        # self.pdf.plotOn(frame,
        #                 ROOT.RooFit.Components(self.bg.pdf.GetName()),
        #                 ROOT.RooFit.LineStyle(ROOT.kDashed),
        #                 ROOT.RooFit.LineColor(ROOT.kBlue))
        # self.pdf.plotOn(frame,
        #                 ROOT.RooFit.Components(self.chib.pdf.GetName()),
        #                 ROOT.RooFit.LineStyle(ROOT.kSolid),
        #                 ROOT.RooFit.LineColor(ROOT.kBlue))
