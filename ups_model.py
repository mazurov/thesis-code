import ROOT
# from AnalysisPython.PyRoUts import hID, cpp, VE

from AnalysisPython.PyRoUts import cpp
CrystalBallDS = cpp.Analysis.Models.CrystalBallDS

from model import BaseModel
import pdg
from IPython import embed as shell  # noqa


class Ups(object):

    def __init__(self, mass, ns):
        mean = pdg.__dict__["UPS%dS" % ns].value()
        sigma = 0.043
        self.mean = ROOT.RooRealVar("m%ds" % ns,
                                    "mean(%d)" % ns, mean, mean - 0.02,
                                    mean + 0.02)
        self.sigma = ROOT.RooRealVar("s%ds" % ns,
                                     "sigma(%d)" % ns,
                                     sigma, sigma - 0.03, sigma + 0.03)

        self.nL = ROOT.RooRealVar("nL%d" % ns, "nL", 1, 1, 5)  # 4
        self.nR = ROOT.RooRealVar("nR%d" % ns, "nR", 10, 1, 10)  # 4

        self.alpha = ROOT.RooRealVar("alpha%d" % ns, "alphaL", 1.6,  # 1.28,
                                     0, 3.5)
        # self.alphaR = ROOT.RooRealVar("alphaR", "alphaR", 1.6,
        #                               0, 3.5)

        self.nL.setConstant(True)
        self.nR.setConstant(True)
        self.alpha.setConstant(True)

        self.pdf = CrystalBallDS("y%ds" % ns,
                                 "CrystalBall(%d)" % ns,
                                 mass,
                                 self.mean,
                                 self.sigma,
                                 self.alpha,
                                 self.nL,
                                 self.alpha,
                                 self.nR
                                 )


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

        self.ups1s = Ups(mass=self.x, ns=1)
        self.ups2s = Ups(mass=self.x, ns=2)
        self.ups3s = Ups(mass=self.x, ns=3)

        self.bg = UpsBackground('Background', self.x)

        self.n1s = ROOT.RooRealVar("N1S", "Signal(Y1S)", 100, 0, 1.e+8)
        self.n2s = ROOT.RooRealVar("N2S", "Signal(Y2S)", 100, 0, 1.e+8)
        self.n3s = ROOT.RooRealVar("N3S", "Signal(Y3S)", 100, 0, 1.e+8)
        self.b = ROOT.RooRealVar("B", "Background", 1e+3, 0, 1.e+8)

        self.alist1 = ROOT.RooArgList(
            self.ups1s.pdf,
            self.ups2s.pdf,
            self.ups3s.pdf,
            self.bg.pdf
        )
        self.alist2 = ROOT.RooArgList(
            self.n1s,
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
