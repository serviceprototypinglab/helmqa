import pandas as pd
import pylab
import seaborn
import os
import sys

FONT = 16

def plot_rates(cmap):
	df = pd.read_csv("changerates.csv")
	df = df.set_index(["#date"])

	ax = df.plot(cmap=cmap, fontsize=FONT)
	ax.set_xlabel("date", fontsize=FONT)
	ax.set_ylabel("chart changes", fontsize=FONT)
	ax.set_title("Change rates of KubeApps Hub", fontsize=FONT)
	ax.legend(fontsize=FONT)

	pylab.setp(ax.xaxis.get_majorticklabels(), rotation=70)
	#ax.set_xticks(range(0, len(df["counter"]), 2))
	pylab.tight_layout()

	#pylab.show()
	pylab.savefig("changerates-plot.png")

def plot_total(cmap):
	df = pd.read_csv("changerates-total.csv", header=None, names=["#date", "total"])
	df = df.set_index(["#date"])

	#df["total"] = df["total"].astype(int)

	dfuniq = None
	if os.path.isfile("changerates-unique.csv"):
		dfuniq = pd.read_csv("changerates-unique.csv")
		dfuniq = dfuniq.set_index(["#date"])

	ax = df.plot(cmap=cmap, ylim=[0, max(df["total"]) + 50], fontsize=FONT)
	ax.set_xlabel("date", fontsize=FONT)
	ax.set_ylabel("total charts", fontsize=FONT)
	ax.set_title("Evolution of KubeApps Hub", fontsize=FONT)
	ax.legend(fontsize=FONT)

	if dfuniq is not None:
		dfuniq.plot(cmap=cmap + "_r", ax=ax, fontsize=FONT)

	pylab.setp(ax.xaxis.get_majorticklabels(), rotation=70)
	#ax.set_xticks(range(0, len(df["counter"]), 2))
	pylab.tight_layout()

	#pylab.show()
	pylab.savefig("changerates-total-plot.png")

if __name__ == "__main__":
	if len(sys.argv) not in (2, 3):
		print("Syntax: {} <command> [<colourmap>]".format(sys.argv[0]), file=sys.stderr)
		print("Commands: rates, total / Colourmaps: e.g. gray, seismic", file=sys.stderr)
		sys.exit(1)

	command = sys.argv[1]
	cmap = "gray"
	if len(sys.argv) == 3:
		cmap = sys.argv[2]

	if command == "rates":
		plot_rates(cmap)
	elif command == "total":
		plot_total(cmap)
	else:
		print("Unknown command.", file=sys.stderr)
