import pandas as pd
import pylab
import seaborn

FONT=16

df = pd.read_csv("changerates.csv")
df = df.set_index(["#date"])

ax = df.plot(cmap="gray", fontsize=FONT)
ax.set_xlabel("date", fontsize=FONT)
ax.set_ylabel("chart changes", fontsize=FONT)
ax.set_title("Change rates of KubeApps Hub", fontsize=FONT)
ax.legend(fontsize=FONT)

pylab.setp(ax.xaxis.get_majorticklabels(), rotation=70)
#ax.set_xticks(range(0, len(df["counter"]), 2))
pylab.tight_layout()

#pylab.show()
pylab.savefig("changerates-plot.png")
