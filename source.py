import AnalysisPython.PyRoUts as pyroot
import tools
from selector import Selector


def dataset(tree, cut, field, has_splot):
    columns = [field] if not has_splot else [
        branch.GetName() for branch in tree.GetListOfBranches()]
    selector = Selector(cut, columns)
    tree.Process(selector)
    return selector.data


def histogram(tree, cut, field, nbins):
    x1, x2 = cut[field]
    ret = pyroot.h(pyroot.hID(), pyroot.hID(), nbins, x1, x2)
    tree.Draw('%s >> %s' % (field, ret.GetName()),
              tools.cut_dict2str(cut), "Setw2")
    return ret

    
