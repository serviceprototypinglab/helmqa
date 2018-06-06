import tarfile
import re
import operator
import sys
import os

def dupefinder_template(s, threshold):
	values = {}
	#print(">>>", s)
	p = re.compile("\{\{.*\}\}")
	s = re.sub(p, "TEMPLATE", s)
	#print(">>>", s)
	for line in s.split("\n"):
		lineparts = line.strip().split(":")
		k, *v = lineparts
		v = ":".join(v).strip()
		#print(k, v)
		values[v] = values.setdefault(v, 0) + 1

	return values

def dupefinder(chartfile, threshold, verbose=False):
	blacklist = ("TEMPLATE", "\"TEMPLATE\"", "'TEMPLATE'", "", "v1", "extensions/v1beta1")

	tgz = False
	if chartfile.endswith(".tgz"):
		tgz = True

	values = {}
	if tgz:
		tar = tarfile.open(chartfile)
	else:
		tar = [x for x in [[os.path.join(root, f) for f in filenames] for root, directories, filenames in os.walk(chartfile)] if x]
		tar = [x for y in tar for x in y]
	for entry in tar:
		if tgz:
			entryname = entry.name
		else:
			entryname = entry
		if "/templates/" in entryname and entryname.endswith(".yaml") and not "/charts/" in entryname:
			if verbose:
				print("parse", entryname)
			if tgz:
				template = tar.extractfile(entryname)
				valuestemplate = dupefinder_template(template.read().decode("utf-8"), threshold)
			else:
				valuestemplate = dupefinder_template(open(entryname).read(), threshold)
			#values.update(valuestemplate)
			for v, count in valuestemplate.items():
				values[v] = values.setdefault(v, 0) + count
		else:
			if verbose:
				print("skip", entryname)

	hitlist = sorted(values.items(), key=operator.itemgetter(1, 0), reverse=True)
	significantlist = [x for x in hitlist if x[1] >= threshold and x[0] not in blacklist]
	return significantlist

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Syntax: {} <helmchartfile>".format(sys.argv[0]), file=sys.stderr)
		sys.exit(1)

	dupeslist = dupefinder(sys.argv[1], 3, verbose=True)

	print("-----------------------------------")
	print("Duplicate values without templates:")
	print("-----------------------------------")
	for v, count in dupeslist:
		print("{:2d} x {}".format(count, v))
