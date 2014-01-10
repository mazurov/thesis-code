import simplejson as json
import tmpl
import tools

from collections import deque
import copy
from IPython import embed as shell  # noqa

import AnalysisPython.PyRoUts as pyroot


class Format(object):

    def __init__(self, value, options):
        self.options = {
            "is_bold": False,
            "span": None,
            "round": None
        }
        self.value = (pyroot.VE(str(value))
                      if isinstance(value, tuple) else value)
        self.options.update(options)

    def __getattr__(self, name):
        if name in self.options:
            return self.options[name]
        raise AttributeError

    def texify(self):
        ret = self.value

        if ret is None:
            return "---"

        if isinstance(ret, float):
            if self.round is not None:
                ret = round(ret, self.round)

        if isinstance(ret, tuple):
            ret = pyroot.VE(str(ret))

        if isinstance(ret, pyroot.VE):
            ret = tools.latex_ve(ret)

        if self.is_bold:
            ret = "\\textbf{%s}" % ret
        return str(ret)


class Value(Format):

    def __init__(self, value, **args):
        super(Value, self).__init__(value=value, options=args)
        if isinstance(self.value, pyroot.VE) and ("syst" in args):
            syst = args["syst"]
            fmt = ("%%.%df" % self.round if self.round
                   else "%f")

            self.value = (
                tools.latex_ve(value) +
                "$\\stat^{+" + fmt % syst[0] + "}_{-" +
                fmt % syst[1] + "}\\syst$")


class HeaderIterator(object):

    def __init__(self, table):
        self.groups = [table]

    def __iter__(self):
        return self

    def next(self):
        ret = []
        for group in self.groups:
            ret += group.subgroups
        if not ret:
            raise StopIteration
        self.groups = ret

        return ret


class RowIterator(object):

    def __init__(self, table, key):
        self.table = table
        self.icell = 0
        self.key = key

        self.cells = []
        queue = deque([self.table])
        while queue:
            group = queue.popleft()
            if group.values:
                self.cells.append(group.values[key])
            else:
                for child in group.subgroups:
                    queue.append(child)

    def __getitem__(self, i):
        if i >= len(self.cells):
            raise StopIteration
        return self.cells[i]


class Group(object):

    def __init__(self, key, title, is_cmidrule=False):
        self.key = key
        self.title = title
        self.is_cmidrule = is_cmidrule

        self.subgroups = []
        self.values = {}

    def add_subgroup(self, key, title, is_cmidrule=False):
        group = Group(key, title, is_cmidrule)
        self.subgroups.append(group)
        return group

    def get_subgroup(self, key):
        for g in self.subgroups:
            if g.key == key:
                return g
        return None

    def add_value(self, key, value, **kwargs):
        if isinstance(value, Value):
            self.values[key] = value
        else:
            self.values[key] = Value(value, **kwargs)

    def cols(self):
        if not self.subgroups:
            return 1
        return reduce(lambda x, y: x + y.cols(), self.subgroups, 0)

    def set_cmidrule(self, flag=True):
        self.is_cmidrule = flag

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


class Row(Format):

    def __init__(self, key, title, **kwargs):
        super(Row, self).__init__(value=title, options=kwargs)
        self.key = key
        self.title = title

    def __str__(self):
        return json.dumps(self.__dict__)


class Line:

    def __str__(self):
        return "line"


class Space:

    def __str__(self):
        return "space"


class Table(Group):

    def __init__(self, title, label, scale=1):
        super(Table, self).__init__(key="table", title=title)
        self.label = label
        self.rows = []
        self.scale = scale

    def add_row(self, key, title, **kwargs):
        self.rows.append(Row(key, title, **kwargs))

    def space(self):
        self.rows.append(Space())

    def line(self):
        if isinstance(self.rows[-1], Space):
            self.rows.pop()
        self.rows.append(Line())

    def iterheader(self):
        return HeaderIterator(table=self)

    def iterrow(self, key):
        return RowIterator(table=self, key=key)

    def __getitem__(self, i):
        if i >= len(self.rows):
            raise StopIteration
        else:
            return self.rows[i]


class SubTables(object):

    def __init__(self, title=None, label=None):
        self.tables = []
        self.title = title
        self.label = label

    def add_table(self, table, title):
        self.tables.append(
            {
                "title": title,
                "table": table
            }
        )


def value2tex(value):
    if isinstance(value.value, pyroot.VE):
        return tools.latex_ve(value.value)


def tex_bold(str):
    return "\\textbf{%s}" % str


def totex(str, is_bold=False):
    if is_bold:
        return tex_bold(str)
    return str


def table2tex(table, has_caption=True):
    header = ""
    for headers in table.iterheader():
        cmidrules = ""
        icol = 1
        for head in headers:
            header += " & "
            if head.cols() > 1:
                header += "\\multicolumn{%d}{c}{" % head.cols()
            header += head.title
            if head.cols() > 1:
                header += "}"
            if head.is_cmidrule:
                cmidrules += "\\cmidrule(r){%d-%d}" % (icol + 1,
                                                       icol + head.cols()
                                                       )
            icol += head.cols()
        header += "\\\\\n"
        if cmidrules:
            header += cmidrules + "\n"

    rows = ""
    for row in table:
        if isinstance(row, Row):
            rows += row.texify()
            for cell in table.iterrow(row.key):
                rows += " & %s" % cell.texify()
            rows += "\\\\\n"
        elif isinstance(row, Space):
            rows += "\n\\rule{0pt}{4ex}"
        elif isinstance(row, Line):
            rows += "\\midrule\n"

    context = {
        "env": "tabular",
        "witdh": "",
        "align": "r" * table.cols(),
        "scale": table.scale,
        "title": table.title,
        "label": table.label,
        "header": header,
        "rows": rows,
        "caption?": has_caption
    }

    tex = tmpl.tex_renderer()
    return tex.render_name("table", context)


def subtables2tex(subtable):
    tables = []
    if len(subtable.tables) < 2:
        return table2tex(subtable.tables[0]["table"])

    for st in subtable.tables:
        tables.append(
            {
                "title": st["title"],
                "tabular": table2tex(st["table"], has_caption=False)
            }
        )

    context = {
        "tables": tables,
        "title": (subtable.title if subtable.title
                  else subtable.tables[0]["table"].title),
        "label": (subtable.label if subtable.label
                  else subtable.tables[0]["table"].label)
    }

    tex = tmpl.tex_renderer()
    return tex.render_name("subtables", context)


class PtTable(Table):

    def __init__(self, title, label, ns, binning, scale=1, maxbins=None,
                 is_cmidrule=True):
        super(PtTable, self).__init__(title=title, label=label, scale=scale)
        cfg = tools.load_config("pttable")
        self.ns = ns
        self.binning = binning
        self.maxbins = maxbins

        title = cfg["title"].format(ns=ns) if ns else cfg["titlemumu"]
        self.ups = self.add_subgroup(key="ups", title=title)

        for bin in binning:
            self.ups.add_subgroup(key=tuple(bin),
                                  title=cfg['range'].format(bin[0], bin[1]),
                                  is_cmidrule=is_cmidrule)

    def get_bin(self, bin):
        return self.ups.get_subgroup(key=tuple(bin))

    def texify(self):
        if self.maxbins > len(self.binning):
            return table2tex(self)

        tables = SubTables()
        ntables = len(self.binning) / self.maxbins
        mod = len(self.binning) % self.maxbins
        for i in range(ntables + (0 if mod == 0 else 1)):
            table = copy.deepcopy(self)
            start_bin = i * self.maxbins
            end_bin = i * self.maxbins + self.maxbins - 1

            table.ups.subgroups = (
                table.ups.subgroups[start_bin:end_bin + 1]
            )
            pt_title = "\\Y%dS" % self.ns if self.ns else "\\mumu"
            title = "$%d < p_T^{%s} < %d \\gevc$" % (
                    self.binning[start_bin][0],
                pt_title,
                self.binning[:end_bin + 1][-1][1]
            )
            tables.add_table(table, title=title)

        return subtables2tex(tables)


class SystTable(PtTable):

    def __init__(self, title, label, ns, nchib, binning, scale=1,
                 maxbins=None):
        super(SystTable, self).__init__(
            title=title, label=label, ns=ns, binning=binning, scale=scale,
            maxbins=maxbins
        )
        self.nchib = nchib

        # cycle throw bins
        for group in self.ups.subgroups:
            for sqs in ["7", "8"]:
                sqsgroup = group.add_subgroup(
                    key="%s" % sqs, title=r"\sqs = %s\tev" % sqs,
                    is_cmidrule=True)
                for np in self.nchib:
                    sqsgroup.add_subgroup(
                        key=str(np), title="$N_{\\chi_{b}(%dP)}$" % np
                    )

    def get_group(self, bin, sqs, np):
        return (
            self.get_bin(bin).get_subgroup(key=str(sqs)).
            get_subgroup(key=str(np))
        )


class SqsTable(PtTable):

    def __init__(self, title, label, ns, binning, scale=1, maxbins=None):
        super(SqsTable, self).__init__(
            title=title, label=label, ns=ns, binning=binning, scale=scale,
            maxbins=maxbins
        )

        # cycle throw bins
        for group in self.ups.subgroups:
            for sqs in ["7", "8"]:
                group.add_subgroup(key="%s" % sqs,
                                   title=r"\sqs = %s\tev" % sqs)

    def get_group(self, bin, sqs):
        if str(sqs) == "2011":
            sqs = "7"
        if str(sqs) == "2012":
            sqs = "8"

        return (
            self.get_bin(bin).get_subgroup(key=str(sqs))
        )
