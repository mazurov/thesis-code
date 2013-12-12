import simplejson as json
import tmpl
import tools

from collections import deque
from IPython import embed as shell  # noqa

import AnalysisPython.PyRoUts as pyroot


class Format(object):

    def __init__(self, value, options):
        self.options = {
            "is_bold": False,
            "span": None
        }
        self.value = value
        self.options.update(options)

    def __getattr__(self, name):
        if name in self.options:
            return self.options[name]
        raise AttributeError

    def texify(self):
        ret = self.value
        if isinstance(ret, pyroot.VE):
            ret = tools.latex_ve(ret)
        if self.is_bold:
            ret = "\\textbf{%s}" % ret
        return ret


class Value(Format):

    def __init__(self, value, **args):
        super(Value, self).__init__(value=value, options=args)


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

    def __init__(self, key, title):
        self.key = key
        self.title = title
        self.is_cmidrule = False

        self.subgroups = []
        self.values = {}

    def add_subgroup(self, key, title):
        group = Group(key, title)
        self.subgroups.append(group)
        return group

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
