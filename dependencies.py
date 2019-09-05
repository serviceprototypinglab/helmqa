import glob
import tarfile
import os.path
import yaml

chartsdir = "../research/longtermtracking/charts/"

cor = {}
incor = {}
ver = {}
nover = []
doubles = []

charts = glob.glob("{}/*.tgz".format(chartsdir))
for chart in sorted(charts):
	print(chart)

	tar = tarfile.open(chart)
	for entry in tar:
		entryname = entry.name
		chartname = entryname.split("/")[0]
		if entryname.endswith("Chart.yaml"):
			print(entryname)
			if entryname.count("/") == 3:
				# correct dependency (e.g. cert-manager/charts/webhook/Chart.yaml)
				depname = entryname.split("/")[2]
				cor[chartname] = cor.get(chartname, []) + [depname]

				f = tar.extractfile(entry)
				y = yaml.load(f)
				if "appVersion" in y:
					ver[depname] = ver.get(depname, []) + [chartname + ":" + str(y["appVersion"])]
				else:
					nover.append(chartname)
			elif entryname.count("/") == 2:
				# incorrect dependency (e.g. cert-manager/webhook/Chart.yaml)
				incor[chartname] = incor.get(chartname, 0) + 1
			elif entryname.count("/") == 1:
				# main chart file
				f = tar.extractfile(entry)
				y = yaml.load(f)
				if "appVersion" in y:
					ver[chartname] = ver.get(chartname, []) + ["chart:" + str(y["appVersion"])]
				else:
					pass
					# TODO register into stats
			else:
				if entryname.count("charts") > 1:
					print("double-dependency!", entryname)
					doubles.append(entryname)
	print("--")

cor_ratio = 100 * len(cor) / len(charts)
incor_ratio = 100 * len(incor) / len(charts)
nover_ratio = 100 * len(nover) / len(cor)

depsdist = {}
for chart in cor:
	depsdist[len(cor[chart])] = depsdist.get(len(cor[chart]), 0) + 1

print("Correct deps among all charts: {:.1f}%".format(cor_ratio), cor)
print("Incorrect deps among all charts: {:.1f}%".format(incor_ratio), incor)
print("#deps distribution:", depsdist)
print("Incorrect dep versions among all charts with deps: {:.1f}%".format(nover_ratio), nover)
print("dep versions:", ver)

total = 0
for verentry in sorted(ver):
	if len(ver[verentry]) > 1:
		print("{:30s}: {}".format(verentry, ver[verentry]))
		total += len(ver[verentry])

count = 0
for verentry in sorted(ver):
	if len(ver[verentry]) > 1:
		for v1 in ver[verentry]:
			if not v1.startswith("chart:"):
				chartname, v2 = v1.split(":")
				if not "chart:" + v2 in ver[verentry]:
					print("* notfound", chartname, "=>", verentry, v2)
					count += 1
print("Total notfound: {:.1f}%".format(100 * count / total))

depcount = {}
for chartname in cor:
	for dep in cor[chartname]:
		depcount[dep] = depcount.get(dep, 0) + 1
print("Most popular dependencies:")
topdeps = sorted(((v, k) for k, v in depcount.items()), reverse=True)
print(topdeps)
print("Double dependencies:", len(doubles))
print(doubles)
