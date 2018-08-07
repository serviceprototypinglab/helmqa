import pandas as pd
import pylab


FONT = 16

df = pd.read_csv("authorsets-email.csv")
df = df.set_index(["#numberofemails"])

ax = df.plot(cmap="jet", fontsize=FONT, style=["-", "--"], figsize=(8.0, 5.5-2))
ax.set_xlabel("numbers of issues informed", fontsize=FONT)
ax.set_ylabel("e-mail addresses", fontsize=FONT)
ax.set_title("Issues detected and informed per unique maintainer in KubeApps Helm charts", fontsize=FONT)
ax.legend(fontsize=FONT)

pylab.tight_layout()

pylab.show()
#pylab.savefig("authorsets-email-plot.png")
