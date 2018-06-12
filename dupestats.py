import os
import json
import glob
import sys

import helmchartsduplicatefinder

def dupestats(path_charts):
	stats_values = []
	stats_dupes = []
	stats_max = []
	alldupes = []
	charts = glob.glob("{}/*.tgz".format(path_charts))
	charts += [x[0] for x in [[root for f in filenames if f == "Chart.yaml"] for root, directories, filenames in os.walk(path_charts)] if x]
	counter = {}
	duplicates = {}
	for chart in charts:
		dupeslist = helmchartsduplicatefinder.dupefinder(chart, 3)
		basechart = os.path.basename(chart)
		print(basechart, dupeslist)
		if dupeslist:
			duplicates[basechart] = dupeslist
		alldupes += dupeslist
		stats_values.append(len(dupeslist))
		stats_dupes.append(sum([x[1] for x in dupeslist]))
		if len(dupeslist) > 0:
			stats_max.append(max([x[1] for x in dupeslist]))
			num = len(dupeslist)
			if not num in counter:
				counter[num] = 0
			counter[num] += 1

	f = open("dupestats_charts.json", "w")
	json.dump(duplicates, f, sort_keys=True)
	f.close()

	print("-----------")
	print("Statistics:")
	print("-----------")

	if len(stats_values):
		avg_values = sum(stats_values) / len(stats_values)
		avg_dupes = sum(stats_dupes) / len(stats_dupes)
		if stats_max:
			avg_max = sum(stats_max) / len(stats_max)
		else:
			avg_max = None
	else:
		print("Incomplete statistics due to empty set.")
		avg_values = None
		avg_dupes = None
		avg_max = None

	print(len(stats_values), "charts analysed")
	print("Total duplicated values", sum(stats_values))
	if avg_values:
		print("Average duplicate values", avg_values)
	print("Total duplicates", sum(stats_dupes))
	if avg_dupes:
		print("Average duplicates", avg_dupes)
		print("Average duplicates per value", avg_dupes / avg_values)
	if stats_max:
		print("Total maximum of dupes", max(stats_max))
	if avg_max:
		print("Average maximum", avg_max)

	allhitlist = sorted(alldupes, key=lambda tup: tup[1], reverse=True)
	print("----------------------------")
	print("Top global duplicate values:")
	print("----------------------------")
	for v, count in allhitlist[:10]:
		print("{:2d} x {}".format(count, v))

	print("------------------------------")
	print("Duplicate values distribution:")
	print("------------------------------")
	print(counter)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Syntax: {} <helmchartdirectory>".format(sys.argv[0]), file=sys.stderr)
		sys.exit(1)

	dupestats(sys.argv[1])
