import tarfile
import sys
import yaml
import glob
import os
import json

class AuthorSet:
	def __init__(self):
		self.sets = {}
		self.references = {}
		self.emails = {}
		self.chartnames = {}
		self.anommcs = []

	def authorset(self, chartfile):
		tgz = False
		if chartfile.endswith(".tgz"):
			tgz = True
		chartname = os.path.basename(chartfile).replace(".tgz", "")

		namecomps = chartname.split("-")
		chartname = ""
		for namecomp in namecomps:
			if namecomp[0].isdigit():
				break
			if chartname:
				chartname += "-"
			chartname += namecomp
		#chartname = "-".join(chartname.split("-")[:-1])

		chartname = chartname.replace("-", "")
		if not chartname in self.chartnames:
			self.chartnames[chartname] = []
		self.chartnames[chartname].append(os.path.basename(chartfile))

		if tgz:
			tar = tarfile.open(chartfile)
		else:
			tar = os.listdir(chartfile)
		maint = None
		for entry in tar:
			if tgz:
				entryname = entry.name
			else:
				entryname = entry
			if entryname.endswith("Chart.yaml") and (not tgz or len(entryname.split("/")) == 2):
				if tgz:
					chartstr = tar.extractfile(entryname).read().decode("utf-8")
				else:
					chartstr = open(os.path.join(chartfile, entryname)).read()
				chartinfo = yaml.load(chartstr)
				if "maintainers" in chartinfo:
					#maint = str(chartinfo["maintainers"])
					maint = ""
					for maintainer in chartinfo["maintainers"]:
						if maint:
							maint += ","
						email = "(none)"
						if "email" in maintainer:
							email = maintainer["email"]
						name = "(none)"
						if "name" in maintainer:
							name = maintainer["name"]
						#identity = name + "[" + email + "]"
						identity = name.replace(" ", "_").replace("-", "")
						maint += identity
						if not identity in self.references:
							self.references[identity] = []
						self.references[identity].append(chartname)
						if not email in self.emails:
							self.emails[email] = []
						if not identity in self.emails[email]:
							self.emails[email].append(identity)
				else:
					maint = None

		if not maint in self.sets:
			self.sets[maint] = []
		self.sets[maint].append(chartname)

	def preprocess(self, chartdir):
		if os.path.isdir(chartdir):
			self.chartfiles = glob.glob("{}/*.tgz".format(chartdir))
			self.chartfiles += [x[0] for x in [[root for f in filenames if f == "Chart.yaml"] for root, directories, filenames in os.walk(chartdir)] if x]
		else:
			self.chartfiles = [chartdir]
		for chartfile in self.chartfiles:
			self.authorset(chartfile)

		for identity in self.references:
			for chartname in self.references[identity]:
				for identity2 in self.references:
					if chartname == identity2:
						if not chartname in self.anommcs:
							self.anommcs.append(chartname)

	def process(self):
		if len(self.references) == 0 and len(self.chartfiles) == 0:
			print("Skipping statistics, no charts or maintainers found.")
			return

		self.maxrefs = 0
		self.maxmaint = 0
		if len(self.references):
			self.maxrefs = max([len(self.references[identity]) for identity in self.references])
			self.maxmaint = max([len(maint.split(",")) for maint in self.sets if maint])

		print("Statistics:")
		print(" charts =", len(self.chartfiles))
		print(" references (maintainers) =", len(self.references))
		print(" maintainer sets =", len(self.sets))
		if len(self.references):
			print(" avg charts/maintainer =", len(self.chartfiles) / len(self.references))
			#print(" max charts/maintainer =", ) # included in extended sets below
			print(" avg charts/maintainer set =", len(self.chartfiles) / len(self.sets))
			print(" max charts/maintainer set =", self.maxrefs)
			print(" avg maintainers/maintainer set =", len(self.references) / len(self.sets))
			print(" max maintainers/maintainer set =", self.maxmaint)
		else:
			print("Skipping some statistics due to lack of maintainer information.")

		print("Anomalies:")
		for anommc in self.anommcs:
			print(" maintainername equals chartname", anommc)
		if len(self.anommcs):
			print(" =", 100 * len(self.anommcs) / len(self.chartfiles), "%")
		has_issue_email = False
		for email in sorted(self.emails):
			if len(self.emails[email]) > 1:
				has_issue_email = True
				print(" same email different usernames", email, ",".join(self.emails[email]))
		if has_issue_email:
			print(" =", 100 * len([x for x in self.emails if len(self.emails[x]) > 1]) / len(self.emails), "%")
		if None in self.sets:
			for chart in self.sets[None]:
				print(" no maintainer for chart", chart)
			print(" =", 100 * len(self.sets[None]) / len(self.chartfiles), "%")
		has_issue_multiple = False
		for chartname in sorted(self.chartnames):
			if len(self.chartnames[chartname]) > 1:
				has_issue_multiple = True
				print(" multiple charts with same name", chartname, ",".join(self.chartnames[chartname]))
		if has_issue_multiple:
			print(" =", 100 * len([x for x in self.chartnames if len(self.chartnames[x]) > 1]) / len(self.chartfiles), "%")

	def processproposals(self):
		chartdest = {}
		maintdest = {}

		for anommc in self.anommcs:
			print(" maintainername equals chartname", anommc)
			if not anommc in chartdest:
				chartdest[anommc] = []
			chartdest[anommc].append("equals")
			if not anommc in maintdest:
				maintdest[anommc] = []
			maintdest[anommc].append("equals")
		for email in sorted(self.emails):
			if len(self.emails[email]) > 1:
				for username in self.emails[email]:
					if not username in maintdest:
						maintdest[username] = []
					maintdest[username].append("same:{}".format(",".join(self.emails[email])))
		if None in self.sets:
			for chart in self.sets[None]:
				if not chart in chartdest:
					chartdest[chart] = []
				chartdest[chart].append("nomaint")
		for chartname in sorted(self.chartnames):
			if len(self.chartnames[chartname]) > 1:
				for chart in self.chartnames[chartname]:
					if not chart in chartdest:
						chartdest[chart] = []
					chartdest[chart].append("multiple:{}".format(",".join(self.chartnames[chartname])))

		f = open("authorsets_charts.json", "w")
		json.dump(chartdest, f, sort_keys=True)
		f.close()
		f = open("authorsets_maint.json", "w")
		json.dump(maintdest, f, sort_keys=True)
		f.close()

		#for maint in maintdest:
		#	for email, identities in self.emails.items():
		#		for identity in identities:
		#			if identity == maint:
		#				print("*", email, maint)
		outmails = {}
		for email in self.emails:
			if not email or email == "(none)":
				continue
			s = []
			for identity in self.emails[email]:
				if identity in maintdest:
					s.append({"ident": identity})
				for reference in self.references[identity]:
					if reference in chartdest:
						s.append({"chart": reference})
			if s:
				outmails[email] = s

		if not os.path.isfile("dupestats_charts.json"):
			print("WARNING: incomplete chart-maintainer e-mail address links, no dupestats found")
		else:
			f = open("dupestats_charts.json")
			ds = json.load(f)
			f.close()

			for email in self.emails:
				if not email or email == "(none)":
					continue
				s = []
				for identity in sorted(self.emails[email]):
					for reference in sorted(self.references[identity]):
						if reference in self.chartnames:
							for chartname in self.chartnames[reference]:
								if chartname in ds:
									s.append({"chart": reference})
				if s:
					if not email in outmails:
						outmails[email] = []
					outmails[email] += s

		if len(outmails):
			print("E-mail issue report statistics:")
			print(" addresses =", len(outmails))
			print(" issues =", sum([len(outmails[x]) for x in outmails]))
			for email in outmails:
				m_s = [list(k.keys())[0] + ":" + list(k.values())[0] for k in outmails[email]]
				m_s = sorted(set(m_s))
				outmails[email] = [{k[0] : k[1]} for k in [x.split(":") for x in m_s]]
			print(" unique issues =", sum([len(outmails[x]) for x in outmails]))

			counter = {}
			for email in outmails:
				num = len(outmails[email])
				if not num in counter:
					counter[num] = 0
				counter[num] += 1
			print(" distribution", counter)

		f = open("authorsets_emails.json", "w")
		json.dump(outmails, f, sort_keys=True)
		f.close()

	def heatmap(self):
		if not self.maxmaint:
			print("Skipping heatmap plot, insufficient information.")
			return
		print("Plotting heatmap...")

		import matplotlib.pyplot as plt
		import seaborn as sns
		import numpy as np

		# FIXME: extra boundary due to spurious exception
		# IndexError: index 21 is out of bounds for axis 1 with size 15
		a = np.zeros([self.maxmaint + 1, self.maxrefs + 1 + 7])

		for maint in self.sets:
			numcharts = len(self.sets[maint])
			if maint:
				nummaints = len(maint.split(","))
			else:
				nummaints = 0
			a[nummaints, numcharts] += 1

		ax = sns.heatmap(a, annot=True, cmap="gray_r")
		ax.set_xlabel("charts")
		ax.set_ylabel("maintainers")
		plt.savefig("authorsets-heatmap.png")

	def dot(self):
		if not len(self.references):
			return

		f = open("authorsets.dot", "w")
		print("digraph authorsets {", file=f)
		for identity in sorted(self.references):
			for chartname in sorted(self.references[identity]):
				print(" {} -> {};".format(identity, chartname), file=f)
		print("}", file=f)
		f.close()

		os.system("dot -Tpng authorsets.dot > authorsets.png")
		os.system("dot -Tpdf authorsets.dot > authorsets.pdf")

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Syntax: {} <helmchartdirectory> <commmand>".format(sys.argv[0]), file=sys.stderr)
		print("Commands: stats, statsplot")
		sys.exit(1)
	command = sys.argv[2]

	aset = AuthorSet()
	if command in ("stats", "statsplot"):
		aset.preprocess(sys.argv[1])
		aset.process()
		aset.processproposals()
	if command == "statsplot":
		aset.heatmap()
		aset.dot()
