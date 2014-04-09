#!/usr/bin/env python


from figure import Plot
from figure import Figure
import tools


class FigureEff(Figure):

    def enter(self, row, col, size, shift, data):
        plot = Plot(file="mc/eff/%s" % data["img"])
        # plot.add_label("Test", (0.5, 0.5))
        # plot.add_label("Vert", (0.5, 0.5), is_vertical=True, font=2)

        plot.add_label(txt="Efficiency, \\%",
                       pos=(0.02, 0.3), is_vertical=True)

        plot.add_label(txt=r"$p_T^{\Y%dS} \left[\gevc\right]$" % data["ns"],
                       pos=(0.45, 0))

        plot.add_label(txt=r"$\chi_b(%dP) \to \Upsilon(%dS) \gamma$" %
                       (data["np"], data["ns"]),
                       pos=(0.4, 0.4))

        plot.add_sqs(pos=(0.4, 0.3))
        return plot.texify(size=size, shift=shift)


def main():
    cfg = tools.load_config("fig_mceff")
    data = cfg["data"]
    pic = FigureEff(title=cfg["title"], label=cfg["label"],
                    size=cfg["size"], ncols=cfg["ncols"], data=data,
                    scale=cfg["scale"])

    print pic.texify()

if __name__ == '__main__':
    main()
