import tarfile
import yaml
import glob
import os
import json


class AuthorSet:

    chartdir = "_charts"
    authorset_charts = "authorsets_charts.json"
    authorset_maint = "authorsets_maint.json"
    authorset_emails = "authorsets_emails.json"
    authorset_heatmap = "authorsets-heatmap.png"
    authorset_dot = "authorsets.dot"
    authorset_png = "authorsets.png"
    authorset_pdf = "authorsets.pdf"
    dupestats_charts = "dupestats_charts.json"

    def __init__(self, chartdir: str = chartdir,
                 authorset_charts: str = authorset_charts,
                 authorset_maint: str = authorset_maint,
                 authorset_email: str = authorset_emails,
                 authorset_heatmap: str = authorset_heatmap,
                 authorset_dot: str = authorset_dot,
                 authorset_png: str = authorset_png,
                 authorset_pdf: str = authorset_pdf,
                 dupestats_charts: str = dupestats_charts):

        self.chartdir = chartdir
        self.sets = {}
        self.references = {}
        self.emails = {}
        self.chartnames = {}
        self.anommcs = []
        self.chartfiles = []
        self.maxrefs = 0
        self.maxmaint = 0
        self.authorset_charts = authorset_charts
        self.authorset_maint = authorset_maint
        self.dupestats_charts = dupestats_charts
        self.authorset_email = authorset_email
        self.authorset_heatmap = authorset_heatmap
        self.authorset_dot = authorset_dot
        self.authorset_png = authorset_png
        self.authorset_pdf = authorset_pdf

    def preprocess(self):
        if os.path.isdir(self.chartdir):
            self.chartfiles = glob.glob(f"{self.chartdir}/*.tgz")
            self.chartfiles += [x[0] for x in [[root for f in filenames if f == "Chart.yaml"]
                                               for root, directories, filenames in os.walk(self.chartdir)] if x]
        else:
            self.chartfiles = [self.chartdir]

        for chartfile in self.chartfiles:
            self.authorset(chartfile)

        for identity in self.references:
            for identity2 in self.references:
                self.anommcs += [chartname for chartname in self.references[identity] if
                                 chartname == identity2 and chartname not in self.anommcs]

    def process(self):
        if len(self.references) == 0 and len(self.chartfiles) == 0:
            print("Skipping statistics, no charts or maintainers found.")
            return

        self.maxrefs = 0
        self.maxmaint = 0

        if len(self.references):
            self.maxrefs = max([len(self.references[identity]) for identity in self.references])
            self.maxmaint = max([len(maint.split(",")) for maint in self.sets if maint])

        self.print_stats()

    def processproposals(self):
        chartdest = {}
        maintdest = {}

        for anommc in self.anommcs:
            print(" maintainername equals chartname", anommc)

            if anommc not in chartdest:
                chartdest[anommc] = []

            chartdest[anommc].append("equals")

            if anommc not in maintdest:
                maintdest[anommc] = []

            maintdest[anommc].append("equals")

        for email in sorted(self.emails):
            if len(self.emails[email]) > 1:
                for username in self.emails[email]:
                    if username not in maintdest:
                        maintdest[username] = []

                    email_list = ",".join(self.emails[email])
                    maintdest[username].append(f"same:{email_list}")

        if None in self.sets:
            for chart in self.sets[None]:
                if chart not in chartdest:
                    chartdest[chart] = []

                chartdest[chart].append("nomaint")

        for chartname in sorted(self.chartnames):
            if len(self.chartnames[chartname]) > 1:
                for chart in self.chartnames[chartname]:
                    if chart not in chartdest:
                        chartdest[chart] = []

                    chart_list = ",".join(self.chartnames[chartname])
                    chartdest[chart].append(f"multiple:{chart_list}")

        with open(self.authorset_charts, "w") as f:
            json.dump(chartdest, f, sort_keys=True)

        with open(self.authorset_maint, "w") as f:
            json.dump(maintdest, f, sort_keys=True)

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

        if not os.path.isfile(self.dupestats_charts):
            print("WARNING: incomplete chart-maintainer e-mail address links, no dupestats found")
        else:
            with open(self.dupestats_charts) as f:
                ds = json.load(f)

            for email in self.emails:
                if not email or email == "(none)":
                    continue

                s = []

                for identity in sorted(self.emails[email]):
                    for reference in sorted(self.references[identity]):
                        if reference in self.chartnames:
                            for chartname in self.chartnames[reference]:
                                if ds:
                                    if chartname in ds[0].keys():
                                        s.append({"chart": reference})
                if s:
                    if email not in outmails:
                        outmails[email] = []

                    outmails[email] += s

        if len(outmails):
            print("E-mail issue report statistics:")
            print(" addresses =", len(outmails))
            print(" issues =", sum([len(outmails[x]) for x in outmails]))

            for email in outmails:
                m_s = [list(k.keys())[0] + ":" + list(k.values())[0] for k in outmails[email]]
                m_s = sorted(set(m_s))
                outmails[email] = [{k[0]:k[1]} for k in [x.split(":") for x in m_s]]

            print(" unique issues =", sum([len(outmails[x]) for x in outmails]))

            counter = {}

            for email in outmails:
                num = len(outmails[email])
                if num not in counter:
                    counter[num] = 0

                counter[num] += 1

            print(" distribution", counter)

        with open(self.authorset_email, "w") as f:
            json.dump(outmails, f, sort_keys=True)

    def heatmap(self):
        if not self.maxmaint:
            print("Skipping heatmap plot, insufficient information.")
            return

        print("Plotting heatmap...")

        import matplotlib
        matplotlib.use('Agg')
        
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np

        a = np.zeros([self.maxmaint + 1, self.maxrefs + 1])

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
        plt.savefig(self.authorset_heatmap)

    def dot(self):
        if not len(self.references):
            return

        with open(self.authorset_dot, "w") as f:
            print("digraph authorsets {", file=f)

            for identity in sorted(self.references):
                for chartname in sorted(self.references[identity]):
                    print(f" {identity} -> {chartname};", file=f)

            print("}", file=f)

        os.system(f"dot -Tpng {self.authorset_dot} > {self.authorset_png}")
        os.system(f"dot -Tpdf {self.authorset_dot} > {self.authorset_pdf}")

    def authorset(self, chartfile):
        tgz = False

        if chartfile.endswith(".tgz"):
            tgz = True

        chartname = os.path.basename(chartfile).replace(".tgz", "")

        namecomps = chartname.split("-")

        chartname = ""

        for namecomp in namecomps:
            if str(namecomp[0]).isdigit():
                break

            if chartname:
                chartname += "-"

            chartname += namecomp

        chartname = chartname.replace("-", "")

        if chartname not in self.chartnames:
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

                        identity = name.replace(" ", "_").replace("-", "")
                        maint += identity

                        if identity not in self.references:
                            self.references[identity] = []

                        self.references[identity].append(chartname)

                        if email not in self.emails:
                            self.emails[email] = []

                        if identity not in self.emails[email]:
                            self.emails[email].append(identity)
                else:
                    maint = None

        if maint not in self.sets:
            self.sets[maint] = []

        self.sets[maint].append(chartname)

    def print_stats(self):
        print("Statistics:")
        print(" charts =", len(self.chartfiles))
        print(" references (maintainers) =", len(self.references))
        print(" maintainer sets =", len(self.sets))

        if len(self.references):
            print(" avg charts/maintainer =", len(self.chartfiles) / len(self.references))
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
            print(" =", 100 * len([x for x in self.chartnames if len(self.chartnames[x]) > 1]) / len(self.chartfiles),
                  "%")
