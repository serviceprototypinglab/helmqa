import pandas as pd
import datetime

startcount = 177

df = pd.read_csv("changerates.csv")
df = df.set_index(["#date"])

def filtered(df, column, mode=None):
	if mode is None:
		dfc = df[column]
	elif mode == "weekday":
		dfc = df[column][((df["weekday"] != 5) & (df["weekday"] != 6))]
	elif mode == "weekend":
		dfc = df[column][((df["weekday"] == 5) & (df["weekday"] == 6))]
	if not len(dfc):
		return 0
	return sum(dfc) / len(dfc)

def printstats(df, mode=None):
	avg_vupdated = filtered(df, "vupdated", mode)
	avg_updated = filtered(df, "updated", mode)
	avg_new = filtered(df, "new", mode)
	avg_removed = filtered(df, "removed", mode)

	print("== Statistics for {} ==".format(mode))
	print("avg vupdated", avg_vupdated)
	print("avg updated", avg_updated)
	print("avg new", avg_new)
	print("avg removed", avg_removed)
	print("-> avg", (avg_vupdated + avg_updated + avg_new + avg_removed) / 4)

df["weekday"] = [datetime.datetime.strptime(x, "%Y-%m-%d").weekday() for x in df.index]

printstats(df)
printstats(df, "weekday")
printstats(df, "weekend")
