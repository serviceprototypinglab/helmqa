import pandas as pd

startcount = 177

df = pd.read_csv("changerates.csv")
df = df.set_index(["#date"])

df["total"] = df["new"].rolling(min_periods=1, window=1).sum() - df["removed"].rolling(min_periods=1, window=1).sum()
df["total"] = df["total"].astype(int) + 177

print(df["total"])

df["total"].to_csv("changerates-total.csv")
