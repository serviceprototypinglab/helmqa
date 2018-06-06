import subprocess
import os
import datetime
import operator

origdir = os.getcwd()
os.chdir("research/longtermtracking")

r = subprocess.run("COLUMNS=200 git log --stat startingpoint..HEAD", shell=True, stdout=subprocess.PIPE)
log = r.stdout.decode("utf-8")

os.chdir(origdir)

date = None
comment = None
dateline = -5
changes = {}
dates = []
correctcommit = False
for idx, logline in enumerate(log.split("\n")):
	if logline.startswith("Date:"):
		dateline = idx
		datestr = ":".join(logline.split(":")[1:]).strip()
		d = datetime.datetime.strptime(datestr, "%a %b %d %H:%M:%S %Y %z")
		date = str(d.date())
		correctcommit = False
	elif idx == dateline + 2:
		comment = logline.strip()
		if comment == "daily helm tracking":
			correctcommit = True
			dates.append(date)
			changes[date] = []
	elif "Bin" in logline and correctcommit:
		change = [x for x in logline.split(" ") if x]
		if "=>" in change:
			changes[date].append((change[2][:-1], int(change[5]), int(change[7])))
		else:
			changes[date].append((change[0], int(change[3]), int(change[5])))

filename = "changerates.csv"
f = open(filename, "w")
f.write("#date,vupdated,updated,new,removed\n")
f.close()

dates.reverse()
touchedcharts = {}
for date in dates:
	adds = {}
	removes = {}
	updates = {}
	vupdates = {}

	print("--", date)
	for chartname, before, after in changes[date]:
		chartbase = chartname.replace(".tgz", "")

		namecomps = os.path.basename(chartbase).split("-")
		chartbase = ""
		for namecomp in namecomps:
			if namecomp[0].isdigit():
				break
			if chartbase:
				chartbase += "-"
			chartbase += namecomp

		semanticchange = "add"
		if before > 0 and after == 0:
			semanticchange = "remove"
		elif before > 0 and after > 0:
			semanticchange = "modify"

		print("*", chartbase, semanticchange)

		if semanticchange == "modify":
			if not chartbase in updates:
				updates[chartbase] = 1
			else:
				updates[chartbase] += 1
		elif semanticchange == "add":
			if chartbase in removes:
				removes[chartbase] -= 1
				if removes[chartbase] == 0:
					del removes[chartbase]
				if not chartbase in vupdates:
					vupdates[chartbase] = 1
				else:
					vupdates[chartbase] += 1
			else:
				if not chartbase in adds:
					adds[chartbase] = 1
				else:
					adds[chartbase] += 1
		elif semanticchange == "remove":
			if chartbase in adds:
				adds[chartbase] -= 1
				if adds[chartbase] == 0:
					del adds[chartbase]
				if not chartbase in vupdates:
					vupdates[chartbase] = 1
				else:
					vupdates[chartbase] += 1
			else:
				if not chartbase in removes:
					removes[chartbase] = 1
				else:
					removes[chartbase] += 1

	print("Changeset", "adds", adds, "removes", removes, "updates", updates, "vupdates", vupdates)

	f = open(filename, "a")
	f.write("{},{},{},{},{}\n".format(date, len(vupdates), len(updates), len(adds), len(removes)))
	f.close()

	consolidated = {}
	consolidated.update(adds)
	consolidated.update(removes)
	consolidated.update(updates)
	consolidated.update(vupdates)

	for chart in consolidated:
		if chart in touchedcharts:
			touchedcharts[chart] += 1
		else:
			touchedcharts[chart] = 1

for chart in touchedcharts:
	touchedcharts[chart] /= len(dates)
#sortednames = sorted(touchedcharts, key=lambda x: touchedcharts[x])
sortednames = [x[0] for x in sorted(touchedcharts.items(), key=operator.itemgetter(1, 0))]

f = open("changerates-charts.txt", "w")
for sortedname in sortednames:
	print("{:50s} {:3.2f}".format(sortedname, touchedcharts[sortedname]), file=f)
basenumber = 177
regcharts = [touchedcharts[x] for x in touchedcharts if touchedcharts[x] > 0.5]
irregcharts = [touchedcharts[x] for x in touchedcharts if touchedcharts[x] <= 0.5]
reg = len(regcharts)
irreg = len(irregcharts)
print("regularly changed (>50% of days): {} / {:3.2f}% ({:3.2f})".format(reg, 100 * reg / basenumber, sum(regcharts) / len(regcharts)), file=f)
print("infrequently changed (>0% of days): {} / {:3.2f}% ({:3.2f})".format(irreg, 100 * irreg / basenumber, sum(irregcharts) / len(irregcharts)), file=f)
print("unchanged (0% of days): {} / {:3.2f}%".format(basenumber - len(sortednames), 100 * (basenumber - len(sortednames)) / basenumber), file=f)
f.close()
