import subprocess
import os
import sys
import datetime
import operator
import pandas as pd


class Changerates:
    def __init__(self, trackingdir=None, startingpoint=None):
        self.trackingdir = trackingdir
        self.startingpoint = startingpoint

    def tracking(self):
        origdir = os.getcwd()
        os.chdir(self.trackingdir)

        cmd = "COLUMNS=200 git log --stat"
        if self.startingpoint:
            cmd = f"{cmd} {self.startingpoint}..HEAD"

        r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
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

        with open(filename, "w") as f:
            f.write("#date,vupdated,updated,new,removed\n")

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
                    if chartbase not in updates:
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
                        if chartbase not in adds:
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

            with open(filename, "a") as f:
                f.write(f"{date},{len(vupdates)},{len(updates)},{len(adds)},{len(removes)}\n")

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

        sortednames = [x[0] for x in sorted(touchedcharts.items(), key=operator.itemgetter(1, 0))]

        with open("changerates-charts.txt", "w") as f:
            for sortedname in sortednames:
                print(f"{sortedname:50s} {touchedcharts[sortedname]:3.2f}", file=f)

            basenumber = 177
            regcharts = [touchedcharts[x] for x in touchedcharts if touchedcharts[x] > 0.5]
            irregcharts = [touchedcharts[x] for x in touchedcharts if touchedcharts[x] <= 0.5]

            reg = len(regcharts)
            irreg = len(irregcharts)

            print(f"regularly changed (>50% of days): {reg}"
                  f" / {100 * reg / basenumber:3.2f}%"
                  f" ({sum(regcharts) / len(regcharts):3.2f})", file=f)

            print(f"infrequently changed (>0% of days): {irreg}"
                  f" / {100 * irreg / basenumber:3.2f}%"
                  f" ({sum(irregcharts) / len(irregcharts):3.2f})", file=f)

            print(f"unchanged (0% of days):"
                  f" {basenumber - len(sortednames)} / { 100 * (basenumber - len(sortednames)) / basenumber:3.2f}%",
                  file=f)

    def producetotal(self, startcount):
        df = pd.read_csv("changerates.csv")
        df = df.set_index(["#date"])

        df["total"] = df["new"].rolling(min_periods=1, window=1000).sum() - df["removed"].rolling(min_periods=1,
                                                                                                  window=1000).sum()
        df["total"] = df["total"].astype(int) + startcount

        print(df["total"])

        df["total"].to_csv("changerates-total.csv")

    def metrics_filtered(df, column, mode=None):
        if mode is None:
            dfc = df[column]
        elif mode == "weekday":
            dfc = df[column][((df["weekday"] != 5) & (df["weekday"] != 6))]
        elif mode == "weekend":
            dfc = df[column][((df["weekday"] == 5) & (df["weekday"] == 6))]
        if not len(dfc):
            return 0
        return sum(dfc) / len(dfc)

    ## I added self to metrics_printstats
    ## Modify later if anything goes wrong!

    def metrics_printstats(self, df, mode=None):
        avg_vupdated = self.metrics_filtered(df, "vupdated", mode)
        avg_updated = self.metrics_filtered(df, "updated", mode)
        avg_new = self.metrics_filtered(df, "new", mode)
        avg_removed = self.metrics_filtered(df, "removed", mode)

        print(f"== Statistics for {mode} ==")
        print("avg vupdated", avg_vupdated)
        print("avg updated", avg_updated)
        print("avg new", avg_new)
        print("avg removed", avg_removed)
        print("-> avg", (avg_vupdated + avg_updated + avg_new + avg_removed) / 4)

    def metrics(self):
        df = pd.read_csv("changerates.csv")
        df = df.set_index(["#date"])

        df["weekday"] = [datetime.datetime.strptime(x, "%Y-%m-%d").weekday() for x in df.index]

        self.metrics_printstats(df)
        self.metrics_printstats(df, "weekday")
        self.metrics_printstats(df, "weekend")

    def unique_getlog(self):
        origdir = os.getcwd()
        os.chdir(self.trackingdir)

        cmd = "COLUMNS=200 git log -p"

        if self.startingpoint:
            cmd = f"{cmd} {self.startingpoint}..HEAD"

        r = subprocess.run(f"{cmd} helmlinks.json", shell=True, stdout=subprocess.PIPE)

        log = r.stdout.decode("utf-8")
        os.chdir(origdir)
        return log

    def unique_parse(log):
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

    def unique_interpolate(changes, changeslist):
        for date in changeslist[:-1]:
            d = datetime.datetime.strptime(date, "%Y-%m-%d").date()

            while True:
                d += datetime.timedelta(days=1)
                ndate = str(d)
                if ndate in changes:
                    break
                changes[ndate] = 0

    def unique(self, startcount):
        changes = self.unique_parse(self.unique_getlog())
        changeslist = sorted(changes)
        self.unique_interpolate(changes, changeslist)
        changeslist = sorted(changes)

        filename = "changerates-unique.csv"
        with open(filename, "w") as f:
            f.write("#date,uniquetotal\n")
            modcount = 0
            for date in changeslist:
                modcount += changes[date]
                f.write(f"{date},{modcount + startcount}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Syntax: {} <command> [<command-args>...]".format(sys.argv[0]), file=sys.stderr)
        print("Commands: tracking, total, metrics, unique", file=sys.stderr)
        sys.exit(1)
    command = sys.argv[1]

    if command == "tracking":
        if len(sys.argv) not in (3, 4):
            print("Syntax: {} tracking <trackingdir> [<startingpoint>]".format(sys.argv[0]), file=sys.stderr)
            sys.exit(1)
        startingpoint = None
        if len(sys.argv) == 4:
            startingpoint = sys.argv[3]
        cr = Changerates(sys.argv[2], startingpoint)
        cr.tracking()

    elif command == "total":
        if len(sys.argv) != 3:
            print("Syntax: {} total <startcount>".format(sys.argv[0]), file=sys.stderr)
            sys.exit(1)
        cr = Changerates()
        cr.producetotal(sys.argv[2])

    elif command == "metrics":
        cr = Changerates()
        cr.metrics()

    elif command == "unique":
        if len(sys.argv) not in (4, 5):
            print("Syntax: {} unique <trackingdir> <startcount> [<startingpoint>]".format(sys.argv[0]), file=sys.stderr)
            sys.exit(1)
        startingpoint = None
        if len(sys.argv) == 5:
            startingpoint = sys.argv[4]
        cr = Changerates(sys.argv[2], startingpoint)
        cr.unique(sys.argv[3])

    else:
        print("Unknown command.", file=sys.stderr)
