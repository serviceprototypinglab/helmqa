import tarfile
#import re
#import operator
import sys
import os
import subprocess

import helmchartsduplicatefinder

def rewritechart(chartfile, dupeslist):
	os.system("rm -rf _rewriter")
	os.makedirs("_rewriter/orig", exist_ok=True)
	os.makedirs("_rewriter/deduped", exist_ok=True)
	tar = tarfile.open(chartfile)
	tar.extractall("_rewriter/orig")
	tar.extractall("_rewriter/deduped")

	for varcounter, (v, count) in enumerate(dupeslist):
		v = v.replace("\\", "\\\\")
		v = v.replace("/", "\\/").replace("'", "'\\''").replace("[", "\\[")
		v = v.replace("TEMPLATE", "")
		cmd = "for i in `find _rewriter/deduped/*/templates/ -name *.yaml`; do sed -i -e 's/: \(.*\){}$/: \\1{{{{ .suggestions.var{} }}}}/' $i; done".format(v, varcounter)
		#print("---> execute", cmd)
		os.system(cmd)

	p = subprocess.run("diff -Nur _rewriter/orig/ _rewriter/deduped/", shell=True, stdout=subprocess.PIPE)
	diff = p.stdout
	os.makedirs("_diffs", exist_ok=True)
	difffile = os.path.join("_diffs", os.path.basename(chartfile).replace(".tgz", "-deduplicated.diff"))
	f = open(difffile, "wb")
	f.write(diff)
	f.close()

	p = subprocess.run("diffstat {} | tail -1 | sed 's/insertions.*//'".format(difffile), shell=True, stdout=subprocess.PIPE)
	lines = p.stdout.decode("utf-8").strip().split(" ")[-1]
	if lines == "changed":
		lines = 0
		extraeffect = 0
	else:
		lines = int(lines)
		extraeffect = lines - sum([x[1] for x in dupeslist])
	print("effect", lines, "= +", extraeffect)

	dirname = os.listdir("_rewriter/deduped")[0]
	f = open("_rewriter/deduped/{}/values.yaml".format(dirname), "a")
	print("", file=f)
	print("suggestions:", file=f)
	for varcounter, (v, count) in enumerate(dupeslist):
		print("  var{}: {}".format(varcounter, v), file=f)
	f.close()

	p = subprocess.run("diff -Nur _rewriter/orig/ _rewriter/deduped/", shell=True, stdout=subprocess.PIPE)
	diff = p.stdout
	f = open(difffile, "wb")
	f.write(diff)
	f.close()

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Syntax: {} <helmchartfile>".format(sys.argv[0]), file=sys.stderr)
		sys.exit(1)

	dupeslist = helmchartsduplicatefinder.dupefinder(sys.argv[1], 3, verbose=False)

	for v, count in dupeslist:
		print("{:2d} x {}".format(count, v))

	rewritechart(sys.argv[1], dupeslist)
