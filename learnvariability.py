import glob
import subprocess
import yaml
import os
import sys
import time

if len(sys.argv) not in (2, 3):
	print("Syntax: {} <helmchartdirectory> [ref-chartsubs.yaml]".format(sys.argv[0]), file=sys.stderr)
	sys.exit(1)

refsubs = None
if len(sys.argv) == 3:
	f = open(sys.argv[2])
	refsubs = yaml.load(f)
	f.close()

chartdir = sys.argv[1]
chartsubs = {}
charts = glob.glob("{}/*.tgz".format(chartdir))
charts += [x[0] for x in [[root for f in filenames if f == "Chart.yaml"] for root, directories, filenames in os.walk(chartdir)] if x]
for chart in charts:
	print("*", chart)

	namecomps = os.path.basename(chart).split("-")
	chartbase = ""
	for namecomp in namecomps:
		if namecomp[0].isdigit():
			break
		if chartbase:
			chartbase += "-"
		chartbase += namecomp

	p1 = subprocess.run("helm template {}".format(chart), shell=True, stdout=subprocess.PIPE)
	time.sleep(1)
	p2 = subprocess.run("helm template {}".format(chart), shell=True, stdout=subprocess.PIPE)
	tmpl1 = p1.stdout.decode("utf-8").split("\n")
	tmpl2 = p2.stdout.decode("utf-8").split("\n")
	for l1, l2 in zip(tmpl1, tmpl2):
		if l1 != l2:
			try:
				k, v = l1.strip().split(":")
			except:
				print("IRREGULAR", l1, l2)
				continue
			v = v.strip()
			if not chartbase in chartsubs:
				chartsubs[chartbase] = {}
			if refsubs and chartbase in refsubs and k in refsubs[chartbase]:
				v = refsubs[chartbase][k]
			chartsubs[chartbase][k] = v
			print("K <{}> V <{}>".format(k, v))

f = open("chartsubs.yaml", "w")
yaml.dump(chartsubs, f)
f.close()

print("Charts with variability: {} ({:3.2f}%)".format(len(chartsubs), 100 * len(chartsubs) / len(charts)))
print("Total variables: {}".format(sum([len(x) for x in chartsubs])))
