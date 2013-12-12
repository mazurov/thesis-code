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
