import pandas as pd
import pylab
import seaborn

FONT=16

df = pd.read_csv("changerates-total.csv", header=None, names=["#date", "total"])
df = df.set_index(["#date"])

#df["total"] = df["total"].astype(int)

ax = df.plot(cmap="gray", ylim=[0, max(df["total"]) + 50], fontsize=FONT)
ax.set_xlabel("date", fontsize=FONT)
ax.set_ylabel("total charts", fontsize=FONT)
ax.set_title("Evolution of KubeApps Hub", fontsize=FONT)
ax.legend(fontsize=FONT)

pylab.setp(ax.xaxis.get_majorticklabels(), rotation=70)
#ax.set_xticks(range(0, len(df["counter"]), 2))
pylab.tight_layout()

#pylab.show()
pylab.savefig("changerates-total-plot.png")
