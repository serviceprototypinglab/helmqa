import tarfile
import re
import operator
import os
import json
import glob


class DupeStats:
    """statistics about duplicate values"""

    blacklist = ("TEMPLATE", "\"TEMPLATE\"", "'TEMPLATE'", "", "v1", "extensions/v1beta1", "|")
    path_charts = "_charts"
    dump_file = "dupestats_charts.json"
    
    def __init__(self, path=path_charts, dump_file=dump_file, verbose=False):
        """
        Keyword arguments:
        path -- path to charts directory (default "_charts")
        verbose -- verbose (default False)
        """
        self.path = path
        self.verbose = verbose
        self.stats_values = []
        self.stats_dupes = []
        self.stats_max = []
        self.alldupes = []
        self.counter = {}
        self.duplicates = {}
        self.avg_values = None
        self.avg_dupes = None
        self.avg_max = None
        self.allhitlist = []
        self.dump_file = dump_file

        if os.path.isdir(f'{self.path}') and os.listdir(f'{self.path}'):
            charts = glob.glob(f'{self.path}/*.tgz')
            charts += [x[0] for x in [[root for f in filenames if f == "Chart.yaml"] for root, directories, filenames in
                                  os.walk(self.path)] if x]
            self.charts = charts
        else:
            print("Charts directory doesn't exist or empty. Exiting!")
            exit(1)

    def duperfinder_helper(self):
        for chartfile in self.charts:
            dupeslist = self.dupefinder(chartfile)
            basechart = os.path.basename(chartfile)

            print(basechart, dupeslist)

            if dupeslist:
                self.duplicates[basechart] = dupeslist

            self.alldupes += dupeslist

            self.stats_values.append(len(dupeslist))
            self.stats_dupes.append(sum([x[1] for x in dupeslist]))

            if len(dupeslist) > 0:
                self.stats_max.append(max([x[1] for x in dupeslist]))

                num = len(dupeslist)

                if num not in self.counter:
                    self.counter[num] = 0
                self.counter[num] += 1

    def dupefinder(self, chartfile, threshold=3):
        """
        Keyword arguments:
        chartfile -- chart to be tested
        threshold -- threshold (default 3)
        """
        tgz = False

        if chartfile.endswith(".tgz"):
            tgz = True

        values = {}

        if tgz:
            tar = tarfile.open(chartfile)
        else:
            tar = [x for x in
                   [[os.path.join(root, f) for f in filenames] for root, directories, filenames in os.walk(chartfile)]
                   if x]
            tar = [x for y in tar for x in y]

        for entry in tar:
            if tgz:
                entryname = entry.name
            else:
                entryname = entry

            if "/templates/" in entryname and entryname.endswith(".yaml") and "/charts/" not in entryname:
                if self.verbose:
                    print("parse", entryname)

                if tgz:
                    template = tar.extractfile(entryname)
                    template_decoded = template.read().decode("utf-8")
                    valuestemplate = self.dupefinder_template(template_decoded)

                else:
                    template_read = open(entryname).read()
                    valuestemplate = self.dupefinder_template(template_read)

                for v, count in valuestemplate.items():
                    values[v] = values.setdefault(v, 0) + count

            else:
                if self.verbose:
                    print("skip", entryname)

        hitlist = sorted(values.items(), key=operator.itemgetter(1, 0), reverse=True)
        significantlist = [x for x in hitlist if x[1] >= threshold and x[0] not in self.blacklist]

        return significantlist

    @staticmethod
    def dupefinder_template(template):
        """
        Keyword arguments:
        template -- template
        """
        values = {}

        p = re.compile("\{\{.*\}\}")
        template = re.sub(p, "TEMPLATE", template)

        for line in template.split("\n"):
            lineparts = line.strip().split(":")
            k, *v = lineparts
            v = ":".join(v).strip()

            values[v] = values.setdefault(v, 0) + 1

        return values

    def dupe_stats(self):
        """statistics about duplicate values"""

        self.duperfinder_helper()

        try:
            os.path.isfile(self.dump_file)

            with open(self.dump_file, 'w') as f:
                json.dump(self.duplicates, f, sort_keys=True)

        except OSError as os_err:
            print(os_err)

        self.print_stats()

    def print_stats(self):
        """Prints statistics"""
        print("-----------")
        print("Statistics:")
        print("-----------")

        if len(self.stats_values):
            self.avg_values = sum(self.stats_values) / len(self.stats_values)
            self.avg_dupes = sum(self.stats_dupes) / len(self.stats_dupes)

            if self.stats_max:
                self.avg_max = sum(self.stats_max) / len(self.stats_max)

            else:
                self.avg_max = None
        else:
            print("Incomplete statistics due to empty set")
            self.avg_values = None
            self.avg_dupes = None
            self.avg_max = None

        print(len(self.stats_values), "charts analysed")

        print("Total duplicated values", sum(self.stats_values))

        if self.avg_values:
            print("Average duplicate values", self.avg_values)

        print("Total duplicates", sum(self.stats_dupes))

        if self.avg_dupes:
            print("Average duplicates", self.avg_dupes)
            print("Average duplicates per value", self.avg_dupes / self.avg_values)

        if self.stats_max:
            print("Total maximum of dupes", max(self.stats_max))

        if self.avg_max:
            print("Average maximum", self.avg_max)

        self.allhitlist = sorted(self.alldupes, key=lambda tup: tup[1], reverse=True)

        print("----------------------------")
        print("Top global duplicate values:")
        print("----------------------------")

        for v, count in self.allhitlist[:10]:
            print(f'{count:2d} x {v}')

        print("------------------------------")
        print("Duplicate values distribution:")
        print("------------------------------")
        print(self.counter)

    def get_charts(self):
        return self.charts
