import AnalysisPython.PyRoUts as pyroot


class MC(object):

    def __init__(self, db, ns, np):
        self.data = db
        self.ns = ns
        self.np = np

    def value(self, *args):
        ret = None
        curr = self.data
        for key in args:
            if not key in curr:
                return None
            curr = curr[key]
            ret = curr
        return pyroot.VE(str(ret))

    def fit_param(self, bin, nb, key):
        return self.value(bin, "chib%d%dp" % (nb, self.np), key)

    def nchib(self, bin, nb):
        return self.fit_param(bin, nb, "N")

    def nups(self, bin, nb):
        return self.value(bin, "ups_chib%d%dp" % (nb, self.np))

    def eff(self, bin, nb=None):
        res = [self.nchib(bin, 1) / self.nups(bin, 1),
               self.nchib(bin, 2) / self.nups(bin, 2)]
        if nb:
            return res[nb - 1]
        else:
            return (res[0] + res[1]) / 2

    def sigma(self, bin):
        return self.fit_param(bin, 1, "sigma")
