import pandas as pd
import sys

startcount = 177

def producetotal(startcount):
	df = pd.read_csv("changerates.csv")
	df = df.set_index(["#date"])

	df["total"] = df["new"].rolling(min_periods=1, window=1000).sum() - df["removed"].rolling(min_periods=1, window=1000).sum()
	df["total"] = df["total"].astype(int) + startcount

	print(df["total"])

	df["total"].to_csv("changerates-total.csv")

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Syntax: {} <startcount>".format(sys.argv[0]), file=sys.stderr)
		sys.exit(1)
	producetotal(sys.argv[1])
