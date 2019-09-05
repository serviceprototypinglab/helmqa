import glob
import tarfile
import os.path
import yaml
import sys

def scandeps(chartsdir, verbose=False):
	cor = {}
	incor = {}
	ver = {}
	nover = []
	doubles = []

	res = {}

	charts = glob.glob("{}/*.tgz".format(chartsdir))
	for chart in sorted(charts):
		if verbose:
			print(chart)

		tar = tarfile.open(chart)
		for entry in tar:
			entryname = entry.name
			chartname = entryname.split("/")[0]
			if entryname.endswith("Chart.yaml"):
				if verbose:
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
						if verbose:
							print("double-dependency!", entryname)
						doubles.append(entryname)
		if verbose:
			print("--")

	cor_ratio = 100 * len(cor) / len(charts)
	incor_ratio = 100 * len(incor) / len(charts)
	nover_ratio = 100 * len(nover) / len(cor)

	depsdist = {}
	for chart in cor:
		depsdist[len(cor[chart])] = depsdist.get(len(cor[chart]), 0) + 1

	res["cor_ratio"] = cor_ratio
	res["incor_ratio"] = incor_ratio
	res["cor"] = cor
	res["incor"] = incor
	res["depsdist"] = depsdist
	res["nover"] = nover
	res["nover_ratio"] = nover_ratio
	res["ver"] = ver

	total = 0
	found = []
	for verentry in sorted(ver):
		if len(ver[verentry]) > 1:
			found.append((verentry, ver[verentry]))
			total += len(ver[verentry])

	count = 0
	notfound = []
	for verentry in sorted(ver):
		if len(ver[verentry]) > 1:
			for v1 in ver[verentry]:
				if not v1.startswith("chart:"):
					chartname, v2 = v1.split(":")
					if not "chart:" + v2 in ver[verentry]:
						notfound.append((chartname, verentry, v2))
						count += 1

	res["found"] = found
	res["notfound"] = notfound
	res["totalnotfound"] = 100 * count / total

	depcount = {}
	for chartname in cor:
		for dep in cor[chartname]:
			depcount[dep] = depcount.get(dep, 0) + 1
	topdeps = sorted(((v, k) for k, v in depcount.items()), reverse=True)

	res["topdeps"] = topdeps
	res["doubles"] = doubles

	return res

def output(res):
	print("Correct deps among all charts: {:.1f}%".format(res["cor_ratio"]), res["cor"])
	print("Incorrect deps among all charts: {:.1f}%".format(res["incor_ratio"]), res["incor"])
	print("#deps distribution:", res["depsdist"])
	print("Incorrect dep versions among all charts with deps: {:.1f}%".format(res["nover_ratio"]), res["nover"])
	print("dep versions:", res["ver"])

	for verentry, ver in res["found"]:
		print("{:30s}: {}".format(verentry, ver))
	for chartname, verentry, v2 in res["notfound"]:
		print("* notfound", chartname, "=>", verentry, v2)
	print("Total notfound: {:.1f}%".format(res["totalnotfound"]))

	print("Most popular dependencies:")
	print(res["topdeps"])
	print("Double dependencies:", len(res["doubles"]))
	print(res["doubles"])

if __name__ == "__main__":
	if len(sys.argv) == 2:
		chartsdir = sys.argv[1]
		res = scandeps(chartsdir)
		output(res)
	else:
		print("Syntax: {} <chartsdir>".format(sys.argv[0]), file=sys.stderr)
