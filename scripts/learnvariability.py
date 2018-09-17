import glob
import subprocess
import yaml
import os
import sys
import time

if len(sys.argv) not in (2, 3):
    print(f"Syntax: {sys.argv[0]} <helmchartdirectory> [ref-chartsubs.yaml]", file=sys.stderr)
    sys.exit(1)

refsubs = None

if len(sys.argv) == 3:
    with open(sys.argv[2]) as f:
        refsubs = yaml.load(f)

chartdir = sys.argv[1]
chartsubs = {}

charts = glob.glob(f"{chartdir}/*.tgz")
charts += [x[0] for x in
           [[root for f in filenames if f == "Chart.yaml"] for root, directories, filenames in os.walk(chartdir)] if x]

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

    p1 = subprocess.run(f"helm template {chart}", shell=True, stdout=subprocess.PIPE)

    time.sleep(1)

    p2 = subprocess.run(f"helm template {chart}", shell=True, stdout=subprocess.PIPE)

    tmpl1 = p1.stdout.decode("utf-8").split("\n")
    tmpl2 = p2.stdout.decode("utf-8").split("\n")

    for l1, l2 in zip(tmpl1, tmpl2):
        if l1 != l2:

            try:
                k, v = l1.strip().split(":")
            except ValueError:
                print("IRREGULAR", l1, l2)
                continue

            v = v.strip()

            if chartbase not in chartsubs:
                chartsubs[chartbase] = {}

            if refsubs and chartbase in refsubs and k in refsubs[chartbase]:
                v = refsubs[chartbase][k]

            chartsubs[chartbase][k] = v

            print(f"K <{k}> V <{v}>")

with open("chartsubs.yaml", "w") as f:
    yaml.dump(chartsubs, f)

print(f"Charts with variability: {len(chartsubs)} ({100 * len(chartsubs) / len(charts):3.2f}%)")
print(f"Total variables: {sum([len(x) for x in chartsubs])}")
