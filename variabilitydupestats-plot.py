import pandas as pd
import pylab
import sys

FONT = 16


def plot_stats(cmap):
    df = pd.read_csv("variabilitydupestats.csv")
    df = df.set_index(["#numberofcharts"])

    ax = df.plot(cmap=cmap, fontsize=FONT, style=["-", "--"], figsize=(8.0, 5.5 - 2))

    # ax = df.plot(cmap="gray", fontsize=FONT, x=df.index, y="numberofdupes")
    # ax = df.plot(cmap="gray", fontsize=FONT, x=df.index, y="numberofvariables", ax=ax)

    ax.set_xlabel("variables and duplicate values", fontsize=FONT)
    ax.set_ylabel("charts", fontsize=FONT)
    ax.set_title("Variable and duplicate value distribution in KubeApps Helm charts", fontsize=FONT)
    ax.legend(fontsize=FONT)

    # pylab.setp(ax.xaxis.get_majorticklabels(), rotation=70)
    ##ax.set_xticks(range(0, len(df["counter"]), 2))

    pylab.tight_layout()

    # pylab.show()

    pylab.savefig("variabilitydupestats-plot.png")


if __name__ == "__main__":
    if len(sys.argv) not in (1, 2):
        print("Syntax: {} [<colourmap>]".format(sys.argv[0]), file=sys.stderr)
        print("Colourmaps: e.g. gray, jet", file=sys.stderr)
        sys.exit(1)

    cmap = "gray"
    if len(sys.argv) == 2:
        cmap = sys.argv[1]

    plot_stats(cmap)
