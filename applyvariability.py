import glob
import subprocess
import yaml
import os
import sys

if len(sys.argv) != 2:
    print(f"Syntax: {sys.argv[0]} <descriptordirectory>", file=sys.stderr)
    sys.exit(1)

with open("chartsubs.yaml") as f:
    chartsubs = yaml.load(f)

descriptors = glob.glob(f"{sys.argv[1]}/*.yaml")

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
            replacer = v.replace("\"", "\\\"")
            p = subprocess.run(f"sed -i -e 's/{k}: \(.*\)/{k}: {replacer}/g' {descriptor}", shell=True)
