import tmpl


latex_font_sizes = {
    1: r'\tiny',
    2: r'\scriptsize',
    3: r'\footnotesize',
    4: r'\small',
    5: r'\normalsize',
    6: r'\large',
    7: r'\Large',
    8: r'\LARGE',
    9: r'\huge',
    10: r'\Huge'
}


class Pos(object):

    def __init__(self, pos):
        self.pos = pos

    def __call__(self, size, shift):
        x, y = self.pos
        x0, y0 = shift
        width, height = size

        return (
            x0 + int(round(width * x, 0)),
            y0 + int(round(height * y, 0)),
        )


class Image(object):

    def __init__(self, filename):
        self.filename = filename

    def texify(self, size, shift):
        x, y = shift
        width, height = size
        return ("\\put({x},{y}){{\\includegraphics*[width={width}mm,"
                "height={height}mm]{{{filename}}}}}".format(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    filename=self.filename
                ))


class Label(object):

    def __init__(self, txt, pos, **kargw):
        self.txt = txt
        self.pos = Pos(pos)

        self.options = {
            "is_vertical": False,
            "font": "",
            "color": ""
        }

        self.options.update(kargw)

    def texify(self, size, shift):
        x, y = self.pos(size, shift)
        # print size, shift, x, y
        font = (latex_font_sizes[self.options['font']]
                if self.options['font'] else "")
        tex = tmpl.tex_renderer()
        context = {
            "txt": self.txt,
            "x": x,
            "y": y,
            "vertical?": self.options["is_vertical"],
            "font": font,
            "color": self.options["color"]
        }

        return tex.render_name("label", context)


class Legenda(object):

    def __init__(self, img, title, pos, **kargw):
        self.img = img
        self.title = title
        self.pos = Pos(pos)

    def texify(self, size, shift):
        x, y = self.pos(size, shift)
        # print size, shift, x, y
        # font = (latex_font_sizes[self.options['font']]
        #         if self.options['font'] else "")
        tex = tmpl.tex_renderer()
        context = {
            "title": self.title,
            "x1": x,
            "x2": x + 5,
            "y": y,
            "img": self.img,
            "color": self.img
        }

        return tex.render_name("legenda", context)


class Plot(object):

    def __init__(self, file):
        self.image = Image(file)
        self.labels = []
        self.legends = []

    def add_label(self, txt, pos, **kargw):
        self.labels.append(Label(txt, pos, **kargw))

    def add_legenda(self, title, img, pos,  **kargw):
        self.labels.append(
            Legenda(title=title, img=img, pos=pos, **kargw)
        )

    def add_sqs(self, pos):
        self.add_legenda(title=r"\sqs=7\tev", img="blue", pos=pos)
        self.add_legenda(title=r"\sqs=8\tev", img="red",
                         pos=(pos[0], pos[1] - 0.08))

    def texify(self, size, shift=(0, 0)):
        width, height = size
        tex = tmpl.tex_renderer()

        labels = []
        for label in self.labels:
            labels.append(label.texify(size, shift))

        context = {
            "image": self.image.texify(size, shift),
            "labels": labels
        }

        return tex.render_name("plot", context)


class Figure(object):

    def __init__(self, data, label, title, size, ncols, scale=1):
        self.size = size
        self.ncols = ncols
        self.data = data
        self.label = label
        self.title = title
        self.scale = scale

    def _right_order(self):
        ret = []
        row = []
        for i, item in enumerate(reversed(self.data)):
            if (not i % self.ncols) and row:
                ret += row
                row = []
            row.insert(0, item)
        if row:
            ret += row
        return ret

    def texify(self):
        width, height = self.size
        l = len(self.data)
        ncols = self.ncols
        nrows = l / ncols + (0 if not l % ncols else 1)

        cell_width = width / ncols
        cell_height = height / nrows

        ret = []

        for i, d in enumerate(self._right_order()):
            row = i / self.ncols
            col = i - row * ncols
            shift = (col * cell_width, row * cell_height)
            ret.append(
                self.enter(row, col, (cell_width, cell_height), shift, d)
            )
        content = "\n".join(ret)

        context = {
            "content": content,
            "width": self.size[0],
            "height": self.size[1],
            "scale": self.scale,
            "caption": self.title,
            "label": self.label
        }

        tex = tmpl.tex_renderer()
        return tex.render_name("figure", context)

    def enter(self, row, col, size, shift, data):
        """ Should redefine """
        # print row, col, size, shift, data
        return ""


def test():
    plot = Plot(file="path/tofile.pdf")
    plot.add_label("Test", (0.5, 0.5))
    plot.add_label("Vert", (0.5, 0.5), is_vertical=True, font=2)
    print plot.texify(size=(75, 60))

    pic = Figure(title="Some title", label="some:label",
                 size=(150, 180), ncols=3, data=range(10))
    print pic.texify()


if __name__ == '__main__':
    test()
