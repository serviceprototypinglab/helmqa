import glob
import subprocess
import yaml
import os
import sys

if len(sys.argv) != 2:
	print("Syntax: {} <descriptordirectory>".format(sys.argv[0]), file=sys.stderr)
	sys.exit(1)

f = open("chartsubs.yaml")
chartsubs = yaml.load(f)
f.close()

descriptors = glob.glob("{}/*.yaml".format(sys.argv[1]))
for descriptor in descriptors:
	print("*", descriptor)

	namecomps = os.path.basename(descriptor).split("-")
	chartbase = ""
	for namecomp in namecomps:
		if namecomp[0].isdigit():
			break
		if chartbase:
			chartbase += "-"
		chartbase += namecomp

	if chartbase in chartsubs:
		for k, v in chartsubs[chartbase].items():
			print("CHARTBASE", chartbase, k, v)
			p = subprocess.run("sed -i -e 's/{}: \(.*\)/{}: {}/g' {}".format(k, k, v.replace("\"", "\\\""), descriptor), shell=True)
