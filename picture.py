import tmpl


class Pos(object):

    def __init__(self, pos):
        self.pos = pos

    def __call__(self, size, shift):
        x, y = self.pos
        x0, y0 = shift
        width, height = size
        print width, height, x, y, x0, y0
        return (
            x0 + round(width * (1 - x), 1),
            y0 + round(height * (1 - y), 1),
        )


class Image(object):

    def __init__(self, filename):
        self.filename = filename

    def texify(self, size, shift):
        x, y = shift
        width, height = size
        return ("\\put({x},{y}){{\\includegraphics*[width={width}mm,"
                "height={height}mm]{{{filename}}}".format(
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

    def texify(self, size, shift):
        x, y = self.pos(size, shift)
        return "\\put({x},{y}){{{txt}}}".format(
            x=x, y=y, txt=self.txt
        )


class Plot(object):

    def __init__(self, file):
        self.image = Image(file)
        self.labels = []
        self.legends = []

    def add_label(self, txt, pos, **kargw):
        self.labels.append(Label(txt, pos, **kargw))

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


def test():
    plot = Plot(file="path/tofile.pdf")
    plot.add_label("Test", (0.5, 0.5))
    print plot.texify(size=(75, 60))


if __name__ == '__main__':
    test()
