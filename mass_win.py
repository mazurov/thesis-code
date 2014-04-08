import tools
import ROOT
import AnalysisPython.PyRoUts as pyroot


def draw(top=350, style=3003):
    axis = []
    for i in range(1, 4):
        cfg = tools.load_config("chib%ds" % i)
        x0, x1 = cfg["cut"]["mups_dtf"]
        axis += [x0, x1]
    h = pyroot.h1_axis(axis)

    for i in [1, 3, 5]:
        h[i] = top

    h.Sumw2(False)
    h.SetFillColor(ROOT.kBlue)
    h.SetFillStyle(style)
    h.Draw("b same")
    
    ROOT.gPad.SaveAs("figs/ups/mass_win.pdf")
    return h


if __name__ == '__main__':
    draw()
