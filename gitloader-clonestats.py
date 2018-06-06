import pandas as pd
import os

df = pd.read_csv("gitloader.csv")

dist = {}
for count in df["chartcount"]:
	if not count in dist:
		dist[count] = 0
	dist[count] += 1

print("max", df["chartcount"].max())
print("avg", df["chartcount"].mean())
print("dist", dist)

threshold = 10
os.makedirs("_gitrepos", exist_ok=True)
for index, row in df.iterrows():
	if row["chartcount"] >= threshold:
		print("clone", row["#repo"], "with", row["chartcount"], "charts...")
		os.system("git clone https://github.com/{} _gitrepos/{}".format(row["#repo"], os.path.basename(row["#repo"])))
