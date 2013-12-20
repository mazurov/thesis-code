import simplejson
import os.path
import shelve

import locale
import ROOT
import PyRoUts as pyroot

locale.setlocale(locale.LC_ALL, 'en_US.utf8')


def json(file):
    return simplejson.load(open(file, "r"))


def load_config(name):
    file_name = os.path.join('configs', '%s.json' % name)
    return json(file_name)


def save_figure(name, canvas=ROOT.gPad):
    pdf_file = os.path.abspath("./figs/%s.pdf" % name)
    # tex_file = os.path.abspath("./figs/tex/%s.tex" % name)
    create_path(pdf_file)
    # create_path(tex_file)

    # ROOT.gStyle.SetPaperSize(10, 10)
    canvas.SaveAs(pdf_file)
    # canvas.SaveAs(tex_file)


def cut_dict2str(fields):
    ret = ""
    prefix = ""
    for field in fields:
        if isinstance(fields[field], tuple) or isinstance(fields[field], list):
            low, high = fields[field]
            if low is not None:
                ret += " %s %s > %.4f" % (prefix, field, low)
                prefix = "&&"
            if high is not None:
                ret += " %s %s < %.4f" % (prefix, field, high)
                prefix = "&&"
        else:
            ret += " %s %s == %.0f" % (prefix, field, fields[field])
            prefix = "&&"
    return ret


def create_path(filename):
    parent = os.path.dirname(filename)
    if not os.path.exists(parent):
        os.makedirs(parent, mode=0o644)


def pdg_round(ve):  # noqa
    value = ve[0]
    error = ve[1]
    """Given a value and an error, round and format them according to the PDG
    rules for significant digits
    """
    def threeDigits(value):
        "extract the three most significant digits and return them as an int"
        return int(("%.2e" % float(error)).split('e')[0].replace('.', '')
                   .replace('+', '').replace('-', ''))

    def nSignificantDigits(threeDigits):
        assert threeDigits < 1000, ("three digits (%d) cannot be larger" +
                                    " than 10^3" % threeDigits)
        if threeDigits < 101:
            return 2  # not sure
        elif threeDigits < 356:
            return 2
        elif threeDigits < 950:
            return 1
        else:
            return 2

    def frexp10(value):
        "convert to mantissa+exp representation (same as frex, but in base 10)"
        valueStr = ("%e" % float(value)).split('e')
        return float(valueStr[0]), int(valueStr[1])

    def nDigitsValue(expVal, expErr, nDigitsErr):
        """
        compute the number of digits we want for the value, assuming we
        keep nDigitsErr for the error
        """
        return expVal - expErr + nDigitsErr

    def formatValue(value, exponent, nDigits, extraRound=0):
        """
        Format the value; extraRound is meant for the special case
        of threeDigits>950
        """
        roundAt = nDigits - 1 - exponent - extraRound
        nDec = roundAt if exponent < nDigits else 0
        if nDec < 0:
            nDec = 0
        grouping = value > 9999
        return locale.format('%.' + str(nDec) + 'f', round(value, roundAt),
                             grouping=grouping)

    tD = threeDigits(error)
    nD = nSignificantDigits(tD)
    expVal, expErr = frexp10(value)[1], frexp10(error)[1]
    extraRound = 1 if tD >= 950 else 0
    return (
        formatValue(value, expVal, nDigitsValue(
            expVal, expErr, nD), extraRound),
        formatValue(error, expErr, nD, extraRound))


def axis2bins(axis):
    ret = []
    for i in range(len(axis) - 1):
        ret.append(tuple([axis[i], axis[i + 1]]))
    return ret


def get_db(name, flag='c'):
    return shelve.open('data/%s.db' % name, flag=flag)


def latex_ve(ve):
    value, error = pdg_round((ve.value(), ve.error()))
    if error != "0.0":
        return "%s $\pm$ %s" % (value, error)
    else:
        return "%s" % value


def latex_ve_pair(p):
    return latex_ve(pyroot.VE(str(p)))


def tree_preselect(tree, cut, select=True):
    list_id = pyroot.rootID()
    tree.Draw(">>%s" % list_id, cut_dict2str(cut), "entrylist")
    lst = ROOT.gROOT.FindObject(list_id)
    if select:
        tree.SetEntryList(lst)
    return lst


def draw_hists(hists, minimum=None):
    ordered = sorted(hists, key=lambda h: -h.GetMaximum())
    y_minimum = (min([h.GetMinimum() for h in hists])
                 if not minimum else minimum)
    opts = "E1"

    for h in ordered:
        h.SetMinimum(y_minimum)
        h.Draw(opts)
        opts = "E1 same"
