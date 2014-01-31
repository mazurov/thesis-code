import ROOT
# from AnalysisPython.PyRoUts import hID, cpp, VE

# from lib import utils
import pdg
from model import BaseModel

from IPython import embed as shell  # noqa

from AnalysisPython.PyRoUts import cpp
PolyPositive = cpp.Analysis.Models.PolyPositive
ExpoPositive = cpp.Analysis.Models.ExpoPositive
CrystalBallDS = cpp.Analysis.Models.CrystalBallDS


class Background(object):

    def __init__(self, dm, dm_begin, dm_end, order):

        self.tau = ROOT.RooRealVar("exp_tau", "exp_tau", -1.5, -20, 1)
        self.phi1 = ROOT.RooRealVar(
            "poly_phi1", "poly_phi1", 0, -3.1415, 3.1415)
        self.phi2 = ROOT.RooRealVar(
            "poly_phi2", "poly_phi2", 0, -3.1415, 3.1415)
        self.phi3 = ROOT.RooRealVar(
            "poly_phi3", "poly_phi3", 0, -3.1415, 3.1415)
        self.phi4 = ROOT.RooRealVar(
            "poly_phi4", "poly_phi4", 0, -3.1415, 3.1415)
        self.phi5 = ROOT.RooRealVar(
            "poly_phi5", "poly_phi5", 0, -3.1415, 3.1415)

        self.alist = ROOT.RooArgList()
        for i in range(order):
            self.alist.add(getattr(self, "phi%d" % (i + 1)))

        self.exp_pdf = ExpoPositive(
            "exp_pdf", "exp_pdf",
            dm, self.tau,
            self.alist,
            dm_begin,
            dm_end)

        self.exp_pdf = PolyPositive(
            "poly_pdf", "poly_pdf",
            dm,
            self.alist,
            dm_begin,
            dm_end)

        self.pdf = self.exp_pdf


class Chib3P(object):

    def __init__(self, dm, sigma, frac):
        m_pdg = pdg.CHIB13P.value()
        self.mean1 = ROOT.RooRealVar("mean_b1_3p", "mean_b1_3p", m_pdg,
                                     m_pdg - 0.1, m_pdg + 0.1)

        diff = pdg.CHIB23P.value() - pdg.CHIB13P.value()
        self.dmb2b1 = ROOT.RooRealVar("dmb2b1_3p", "dmb2b1_3p", diff)
        self.dmb2b1.setConstant(True)

        alistb2b1 = ROOT.RooArgList(self.mean1, self.dmb2b1)
        self.mean2 = ROOT.RooFormulaVar("mean_b2_3p", "mean_b2_3p",
                                        "%s+%s" % (self.mean1.GetName(),
                                                   self.dmb2b1.GetName()
                                                   ),
                                        alistb2b1)

        self.sigma = ROOT.RooRealVar("sigma_b1_3p", "sigma_b1_3p",
                                     0.02,
                                     0.02 - 0.015,
                                     0.02 + 0.015)
        if sigma:
            self.sigma.fix(sigma)

        self.n = ROOT.RooRealVar("n3", "n3", 5, 1, 20)
        self.a = ROOT.RooRealVar("a3", "a3", -1.25, -3.5, -1)
        self.n.setConstant(True)
        self.a.setConstant(True)

        self.pdf1 = ROOT.RooCBShape("cb1_3",
                                    "CrystalBall_b1(3P)",
                                    dm,
                                    self.mean1,
                                    self.sigma,
                                    self.a,
                                    self.n)

        self.pdf2 = ROOT.RooCBShape("cb2_3",
                                    "CrystalBall_b2(3P)",
                                    dm,
                                    self.mean2,
                                    self.sigma,
                                    self.a,
                                    self.n)
        self.frac = ROOT.RooRealVar("frac3", "frac3", frac, 0, 1)
        self.frac.setConstant(True)
        self.pdf = ROOT.RooAddPdf("cb3", "cb3", self.pdf1, self.pdf2,
                                  self.frac)


class ChibModel(BaseModel):

    def __init__(self, canvas, data, binning,
                 user_labels=None, is_pull=True,
                 frac=0.5,
                 bgorder=2,
                 sigma=None,
                 mean_3p=pdg.CHIB13P):
        super(ChibModel, self).__init__(canvas=canvas,
                                        data=data,
                                        interval=binning[1:],
                                        xfield="dmplusm3s",
                                        nbins=binning[0],
                                        user_labels=user_labels,
                                        is_pull=is_pull)

        self.chib3p = Chib3P(dm=self.x, sigma=sigma, frac=frac)

        self.bg = Background(dm=self.x, dm_begin=self.x0, dm_end=self.x1,
                             order=bgorder)

        self.b = ROOT.RooRealVar("B", "Background", 1e+6, 0, 1.e+8)
        self.n3p = ROOT.RooRealVar("N3P", "N3P", 1e+1, 0, 1.e+7)

        self.alist1 = ROOT.RooArgList(self.bg.pdf, self.chib3p.pdf)

        self.alist2 = ROOT.RooArgList(self.b, self.n3p)

        self.pdf = ROOT.RooAddPdf("model", "model", self.alist1, self.alist2)

    def labels(self):
        frame = self.frame
        frame.SetTitle("")
        frame.GetXaxis().SetTitle("")
        frame.GetYaxis().SetTitle("")
        # frame.GetXaxis().SetTitle("m(#mu^{+}#mu^{-}#gamma) - "
        # "m(#mu^{+ }#mu^{-}) [GeV/c^{2}]")
        # self.candidates()

    def curves(self):
        frame = self.frame
        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.bg.pdf.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kBlue))

        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib3p.pdf1.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kMagenta + 1))
        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib3p.pdf2.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kGreen + 1))

    def sPlot(self):
        splot = ROOT.RooStats.SPlot("sPlot_h_fit",
                                    "sPlot",
                                    self.data,
                                    self.pdf, self.alist2)
        self.splots += [splot]
        return splot
