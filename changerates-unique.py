import subprocess
import os
import datetime
import operator

startcount = 154

def getlog():
	origdir = os.getcwd()
	os.chdir("research/longtermtracking")
	r = subprocess.run("COLUMNS=200 git log -p startingpoint..HEAD helmlinks.json", shell=True, stdout=subprocess.PIPE)
	log = r.stdout.decode("utf-8")
	os.chdir(origdir)
	return log

def parse(log):
	date = None
	comment = None
	dateline = -5
	changes = {}
	dates = []
	correctcommit = False
	predate = None
	for idx, logline in enumerate(log.split("\n")):
		if logline.startswith("Date:"):
			dateline = idx
			datestr = ":".join(logline.split(":")[1:]).strip()
			d = datetime.datetime.strptime(datestr, "%a %b %d %H:%M:%S %Y %z").date()
			date = str(d)
			correctcommit = False
			predate = d - datetime.timedelta(days=1)
		elif idx == dateline + 2:
			comment = logline.strip()
			if comment == "daily helm tracking":
				correctcommit = True
				dates.append(date)
				changes[date] = 0
		elif correctcommit:
			if logline.startswith("+") and "/stable/" in logline:
				changes[date] += 1
			elif logline.startswith("-") and "/stable/" in logline:
				changes[date] -= 1

	predate = str(predate)
	changes[predate] = 0

	return changes

def interpolate(changes, changeslist):
	for date in changeslist[:-1]:
		d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
		while True:
			d += datetime.timedelta(days=1)
			ndate = str(d)
			if ndate in changes:
				break
			changes[ndate] = changes[date]

changes = parse(getlog())
changeslist = sorted(changes)
interpolate(changes, changeslist)
changeslist = sorted(changes)

filename = "changerates-unique.csv"
f = open(filename, "w")
f.write("#date,uniquetotal\n")
for date in changeslist:
	f.write("{},{}\n".format(date, changes[date] + startcount))
f.close()
