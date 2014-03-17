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

        self.pdf = self.exp_pdf


class Chib1P(object):

    def __init__(self, dm, frac, sigma=None):
        m_pdg = pdg.CHIB11P.value()
        self.mean1 = ROOT.RooRealVar("mean_b1_1p", "mean_b1_1p", m_pdg,
                                     m_pdg - 0.05, m_pdg + 0.05)
        # self.mean1.setConstant(True)
        diff = pdg.CHIB21P.value() - pdg.CHIB11P.value()
        self.dmb2b1 = ROOT.RooRealVar("dmb2b1_1p", "dmb2b1_1p", diff)
        self.dmb2b1.setConstant(True)

        alistb2b1 = ROOT.RooArgList(self.mean1, self.dmb2b1)
        self.mean2 = ROOT.RooFormulaVar("mean_b2_1p", "mean_b2_1p",
                                        "%s+%s" % (self.mean1.GetName(),
                                                   self.dmb2b1.GetName()
                                                   ),
                                        alistb2b1)

        self.sigma1 = ROOT.RooRealVar("sigma_b1_1p", "sigma_b1_1p",
                                      0.024,
                                      0.024 - 0.01,
                                      0.024 + 0.01)
        if sigma:
            self.sigma1.fix(sigma)

        self.sdiffb2b1 = ROOT.RooRealVar("sdiffb2b1", "sdiffb2b1",
                                         1.05,
                                         1,
                                         1.08)
        self.sdiffb2b1.setConstant(True)
        alist_s_b2b1 = ROOT.RooArgList(self.sigma1, self.sdiffb2b1)
        self.sigma2 = ROOT.RooFormulaVar("sigma_b2_1p", "sigma_b2_1p",
                                         "%s*%s" % (self.sigma1.GetName(),
                                                    self.sdiffb2b1.GetName()
                                                    ),
                                         alist_s_b2b1)

        self.n = ROOT.RooRealVar("n1", "n1", 5, 1, 5)
        self.n.setConstant(True)
        self.a = ROOT.RooRealVar("a1", "a1", -1.1, -5, 0)
        self.a.setConstant(True)

        self.pdf1 = ROOT.RooCBShape("cb1_1", "cb1_1", dm, self.mean1,
                                    self.sigma1, self.a, self.n)
        self.pdf2 = ROOT.RooCBShape("cb2_1", "cb2_1", dm, self.mean2,
                                    self.sigma2, self.a, self.n)

        self.frac = ROOT.RooRealVar("frac1", "frac1", frac, 0, 1)
        self.frac.setConstant(True)
        
        self.pdf = ROOT.RooAddPdf("cb1", "cb1", self.pdf1, self.pdf2,
                                  self.frac)


class Chib2P(object):

    def __init__(self, dm, mean_1p, sigma1, sfrac, frac):
        # dm_pdg = pdg.DM1S[2].value()

        diff = pdg.CHIB12P - pdg.CHIB11P
        self.dm1p = ROOT.RooRealVar("dm_b12p_b11p", "dm_b12p_b11p",
                                    diff, diff - 0.05, diff + 0.05)
        self.dm1p.setConstant(True)

        alist = ROOT.RooArgList(mean_1p, self.dm1p)
        self.mean1 = ROOT.RooFormulaVar("mean_b1_2p", "mean_b1_2p",
                                        "%s+%s" %
                                        (mean_1p.GetName(),
                                         self.dm1p.GetName()), alist)

        diff = pdg.CHIB22P.value() - pdg.CHIB12P.value()
        self.dmb2b1 = ROOT.RooRealVar("dmb2b1_2p", "dmb2b1_2p", diff)
        self.dmb2b1.setConstant(True)

        alistb2b1 = ROOT.RooArgList(self.mean1, self.dmb2b1)
        self.mean2 = ROOT.RooFormulaVar("mean_b2_2p", "mean_b2_2p",
                                        "%s+%s" % (self.mean1.GetName(),
                                                   self.dmb2b1.GetName()
                                                   ),
                                        alistb2b1)

        if sfrac:
            self.sfrac = ROOT.RooRealVar("sfrac2p1p", "sfrac2p1p", 1.6, 1, 3)
            self.sfrac.fix(sfrac)

            alist = ROOT.RooArgList(self.sfrac, sigma1)
            self.sigma = ROOT.RooFormulaVar("sigma2", "sigma2",
                                            "%s*%s" % (self.sfrac.GetName(),
                                                       sigma1.GetName()), alist)
        else:
            self.sigma = ROOT.RooRealVar("sigma_b1_2p", "sigma_b1_2p",
                                         0.03,
                                         0.03 - 0.02,
                                         0.03 + 0.02)

        self.n = ROOT.RooRealVar("n2", "n2", 5, 1, 5)
        self.a = ROOT.RooRealVar("a2", "a2", -1.1, -3.5, 0)  # -1.23
        self.n.setConstant(True)
        self.a.setConstant(True)

        self.pdf1 = ROOT.RooCBShape("cb1_2",
                                    "CrystalBall_b1(2P)",
                                    dm,
                                    self.mean1,
                                    self.sigma,
                                    self.a,
                                    self.n)

        self.pdf2 = ROOT.RooCBShape("cb2_2",
                                    "CrystalBall_b2(2P)",
                                    dm,
                                    self.mean2,
                                    self.sigma,
                                    self.a,
                                    self.n)
        self.frac = ROOT.RooRealVar("frac2", "frac2", frac, 0, 1)
        self.frac.setConstant(True)
        self.pdf = ROOT.RooAddPdf("cb2", "cb2", self.pdf1, self.pdf2,
                                  self.frac)


class Chib3P(object):

    def __init__(self, dm, mean_1p, sigma1, mean_3p, sfrac, frac):

        diff = mean_3p - pdg.CHIB11P
        self.dm1p = ROOT.RooRealVar("dm_b13p_b11p", "dm_b13p_b11p",
                                    diff, diff - 0.05, diff + 0.05)
        self.dm1p.setConstant(True)

        alist = ROOT.RooArgList(mean_1p, self.dm1p)
        self.mean1 = ROOT.RooFormulaVar("mean_b1_3p", "mean_b1_3p",
                                        "%s+%s" %
                                        (mean_1p.GetName(),
                                         self.dm1p.GetName()), alist)

        diff = pdg.CHIB23P.value() - pdg.CHIB13P.value()
        self.dmb2b1 = ROOT.RooRealVar("dmb2b1_3p", "dmb2b1_3p", diff)
        self.dmb2b1.setConstant(True)

        alistb2b1 = ROOT.RooArgList(self.mean1, self.dmb2b1)
        self.mean2 = ROOT.RooFormulaVar("mean_b2_3p", "mean_b2_3p",
                                        "%s+%s" % (self.mean1.GetName(),
                                                   self.dmb2b1.GetName()
                                                   ),
                                        alistb2b1)

        if sfrac:
            self.sfrac = ROOT.RooRealVar("sfrac3p1p", "sfrac3p1p", 2, 1, 3)
            if sfrac:
                self.sfrac.fix(sfrac)
            alist = ROOT.RooArgList(self.sfrac, sigma1)
            self.sigma = ROOT.RooFormulaVar(
                "sigma3", "sigma3", "%s*%s" % (self.sfrac.GetName(),
                                               sigma1.GetName()), alist)
        else:
            self.sigma = ROOT.RooRealVar("sigma_b1_3p", "sigma_b1_3p",
                                         0.04,
                                         0.05 - 0.04,
                                         0.05 + 0.04)

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
                 frac=(0.5, 0.5, 0.5),
                 bgorder=3,
                 sigma=None,
                 sfracs=(None, None),
                 mean_3p=pdg.CHIB13P,
                 has_3p=True):
        super(ChibModel, self).__init__(canvas=canvas,
                                        data=data,
                                        interval=binning[1:],
                                        xfield="dmplusm1s",
                                        nbins=binning[0],
                                        user_labels=user_labels,
                                        is_pull=is_pull)
        sfracs2, sfracs3 = sfracs
        self.chib1p = Chib1P(dm=self.x, frac=frac[0], sigma=sigma)

        self.chib2p = Chib2P(dm=self.x,
                             mean_1p=self.chib1p.mean1,
                             sigma1=self.chib1p.sigma1,
                             sfrac=sfracs2,
                             frac=frac[1])
        self.chib3p = Chib3P(dm=self.x,
                             mean_1p=self.chib1p.mean1,
                             sigma1=self.chib1p.sigma1,
                             mean_3p=mean_3p,
                             sfrac=sfracs3,
                             frac=frac[2])

        self.bg = Background(dm=self.x, dm_begin=self.x0, dm_end=self.x1,
                             order=bgorder)

        self.b = ROOT.RooRealVar("B", "Background", 1e+6, 0, 1.e+8)
        self.n1p = ROOT.RooRealVar("N1P", "N1P", 1e+3, 0, 1.e+7)
        self.n2p = ROOT.RooRealVar("N2P", "N2P", 1e+2, 0, 1.e+7)
        self.n3p = ROOT.RooRealVar("N3P", "N3P", 1e+1, 0, 1.e+7)

        self.alist1 = ROOT.RooArgList(
            self.bg.pdf,
            self.chib1p.pdf,
            self.chib2p.pdf
        )

        self.alist2 = ROOT.RooArgList(
            self.b,
            self.n1p,
            self.n2p
        )

        if has_3p:
            self.alist1.add(self.chib3p.pdf)
            self.alist2.add(self.n3p)

        self.pdf = ROOT.RooAddPdf("model", "model",
                                  self.alist1,
                                  self.alist2)

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
                        ROOT.RooFit.Components(self.chib1p.pdf1.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kMagenta + 1))
        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib1p.pdf2.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kGreen + 1))

        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib2p.pdf1.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kMagenta + 1))

        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib2p.pdf2.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kGreen + 1))

        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib3p.pdf1.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kMagenta + 1))
        self.pdf.plotOn(frame,
                        ROOT.RooFit.Components(self.chib3p.pdf2.GetName()),
                        ROOT.RooFit.LineStyle(ROOT.kDashed),
                        ROOT.RooFit.LineColor(ROOT.kGreen + 1))

        # self.pdf.plotOn(frame,
        #                 ROOT.RooFit.Components(self.chib3p.pdf2.GetName()),
        #                 ROOT.RooFit.LineStyle(ROOT.kDashed),
        #                 ROOT.RooFit.LineColor(ROOT.kGreen + 1))

    def sPlot(self):
        splot = ROOT.RooStats.SPlot("sPlot_h_fit",
                                    "sPlot",
                                    self.data,
                                    self.pdf, self.alist2)
        self.splots += [splot]
        return splot
