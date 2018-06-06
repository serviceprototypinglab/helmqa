import pandas as pd
import pylab
import seaborn

FONT=16

df = pd.read_csv("variabilitydupestats.csv")
df = df.set_index(["#numberofcharts"])

ax = df.plot(cmap="jet", fontsize=FONT, style=["-", "--"], figsize=(8.0, 5.5-2))
#ax = df.plot(cmap="gray", fontsize=FONT, x=df.index, y="numberofdupes")
#ax = df.plot(cmap="gray", fontsize=FONT, x=df.index, y="numberofvariables", ax=ax)
ax.set_xlabel("variables and duplicate values", fontsize=FONT)
ax.set_ylabel("charts", fontsize=FONT)
ax.set_title("Variable and duplicate value distribution in KubeApps Helm charts", fontsize=FONT)
ax.legend(fontsize=FONT)

#pylab.setp(ax.xaxis.get_majorticklabels(), rotation=70)
##ax.set_xticks(range(0, len(df["counter"]), 2))
pylab.tight_layout()

pylab.show()
#pylab.savefig("variabilitydupestats-plot.png")
