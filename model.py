import ROOT
from IPython import embed as shell  # noqa
import re
NUMCPU = 7


class BaseModel(object):

    def __init__(self, canvas, interval, xfield, data=None, x=None, nbins=100,
                 user_labels=None, is_pull=True):
        self.x0, self.x1 = interval
        self.perbin = (self.x1 - self.x0) * 1000 / nbins
        self.xfield = xfield
        self.x = x if x else ROOT.RooRealVar(xfield, xfield, self.x0, self.x0,
                                             self.x1)
        self.nbins = nbins
        self.canvas = canvas
        self.data = data
        self.is_pull = is_pull

        self.chi2 = -1
        self.chi2roofit = -1
        self.prob = 0
        self.fit = None
        self.frame = None
        self.user_labels = user_labels

        self.splots = []

    def fitData(self):
        if isinstance(self.data, ROOT.TH1D):
            self._fitHisto()
        else:
            self._fitTo()
        return self.status

    def _fitHisto(self):
        """
        Fit the histogram
        """
        lst = ROOT.RooArgList(self.x)
        imp = ROOT.RooFit.Import(self.data)
        hset = ROOT.RooDataHist(
            "ds", "Data set for histogram '%s'" % self.data.GetTitle(),
            lst, imp)

        self.fit = self.pdf.fitTo(hset, ROOT.RooFit.Save())
        self.frame = self.x.frame()

        hset.plotOn(self.frame)

        self.after_fit()

    def _fitTo(self):
        self.fit = self.pdf.fitTo(self.data,
                                  ROOT.RooFit.Save(),
                                  ROOT.RooFit.NumCPU(NUMCPU)
                                  )

        self.frame = self.x.frame()
        self.data.plotOn(self.frame, ROOT.RooFit.Binning(self.nbins))

        self.after_fit()

    def after_fit(self):
        self._plot()
        self._eval_chi2()
        self._fit_status()
        self.labels()
        if self.user_labels:
            self.canvas.cd(1)
            self.user_labels(self)
            self.canvas.cd()

    def labels(self):
        assert False, "Labels don't implemented"
        pass

    def curves(self):
        assert False, "Curves don't implemented"
        pass

    def draw_after(self):
        pass

    def _plot(self):
        frame = self.frame
        self.curves()
        self.pdf.plotOn(frame, ROOT.RooFit.Name("model"),
                        ROOT.RooFit.LineColor(ROOT.kRed))
        frame.drawAfter("model", "h_ds")
        frame.drawAfter("model_Comp[bg]", "h_ds")
        # self.draw_after()

        if self.is_pull:
            self.hpull = frame.pullHist("h_ds", "model")

            frame_pull = self.x.frame(ROOT.RooFit.Title("Pull Distribution"))

            frame_pull.SetMinimum(-5)
            frame_pull.SetMaximum(5)
            frame_pull.SetNdivisions(8, "y")
            frame_pull.SetNdivisions(0, "x")
            frame_pull.GetYaxis().SetLabelSize(0.1)
            frame_pull.GetYaxis().SetTitle("")
            # frame_pull.GetYaxis().SetTitleSize(0.2)
            # frame_pull.GetYaxis().SetTitleOffset(0.1)
            frame_pull.GetXaxis().SetTitle("")
            frame_pull.addPlotable(self.hpull, "P")

            self.canvas.Clear()
            self.canvas.Divide(1, 2)

            pad = self.canvas.cd(1)
            pad.SetPad(0, 0.2, 1, 1)
            frame.Draw()

            pad = self.canvas.cd(2)
            # pad.SetGridy(True)
            pad.SetPad(0, 0, 1, 0.18)

            xMin = frame_pull.GetXaxis().GetXmin()
            xMax = frame_pull.GetXaxis().GetXmax()
            self.hpull_uppLine = ROOT.TLine(xMin, 3, xMax, 3)
            self.hpull_midLine = ROOT.TLine(xMin, 0, xMax, 0)
            self.hpull_lowLine = ROOT.TLine(xMin, -3, xMax, -3)
            self.hpull_uppLine.SetLineColor(ROOT.kBlue)
            self.hpull_midLine.SetLineColor(ROOT.kRed)
            self.hpull_lowLine.SetLineColor(ROOT.kBlue)
            self.hpull_uppLine.SetLineWidth(2)
            self.hpull_midLine.SetLineWidth(2)
            self.hpull_lowLine.SetLineWidth(2)
            # self.hpull_uppLine.SetLineStyle(ROOT.kDashed),
            # self.hpull_lowLine.SetLineStyle(ROOT.kDashed),

            frame_pull.Draw()
            self.hpull_uppLine.Draw()
            self.hpull_midLine.Draw()
            self.hpull_lowLine.Draw()

            self.frame_pull = frame_pull
            self.canvas.cd()
        else:  # no pull
            frame.Draw()

    def _eval_chi2(self):
        pdf_name = "model"

        nbins = ROOT.gROOT.FindObject("h_ds").GetN()
        self.ndf = nbins - len(self.fit.params())

        # self.chi2roofit = self.frame.chiSquare(len(self.fit.params()))
        # self.chi2 = self._chi2()
        # self.chi2ndf = self.chi2 / self.ndf
        # self.prob = ROOT.TMath.Prob(self.chi2, self.ndf)

        self.chi2 = self.frame.chiSquare(pdf_name, "h_ds") * nbins

        self.chi2ndf = self.frame.chiSquare(
            pdf_name, "h_ds", len(self.fit.params()))

        self.prob = ROOT.TMath.Prob(self.chi2, self.ndf)

    def _chi2(self):
        ret = 0
        for e in self.hpull:
            ret += self.hpull[e][1] ** 2
        return ret

    def _fit_status(self):
        self.status = self.fit.covQual() == 3

    def candidates(self):
        yaxis = self.frame.GetYaxis()
        res = re.findall(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?',
                         yaxis.GetTitle())
        yaxis.SetTitle("Candidates / ( %d MeV/c^{2} )" %
                       (self.perbin))

    def params(self):
        return dict(
            [(p.GetName(), (p.getVal(), p.getError()))
             for p in self.fit.floatParsFinal()]
            +
            [(p.GetName(), p.getVal()) for p in self.fit.constPars()]
            +
            [("chi2", self.chi2),
             ("ndf", self.ndf),
             ("chi2ndf", self.chi2ndf), ("prob", self.prob),
             ("perbin", self.perbin)]
        )

    def save_image(self, path):
        self.canvas.SaveAs(path)

    def __str__(self):
        ret = str(self.fit) + "\n"
        ret += "Chi2 = %.2f\n" % self.chi2
        ret += "ndf = %.2f\n" % self.ndf
        ret += "Chi2/ndf = %.2f\n" % self.chi2ndf
        ret += "Probability = %.3f%%\n" % (self.prob * 100)
        ret += "Bin size = %.2f MeV" % self.perbin
        return ret
