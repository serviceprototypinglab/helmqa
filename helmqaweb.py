import flask
import json
import os
import time
import copy
import subprocess
from flask import request, jsonify

app = flask.Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


class HelmQA:
    def __init__(self):
        try:
            self.initfiles()
        except:
            self.configured = False
        else:
            self.configured = True

    def initfiles(self):
        with open("authorsets_charts.json") as f:
            self.charts = json.load(f)

        with open("authorsets_maint.json") as f:
            self.maintainers = json.load(f)

        with open("dupestats_charts.json") as f:
            self.dupes = json.load(f)

    @staticmethod
    def datapoint():
        st = os.stat("authorsets_charts.json")
        return time.strftime("%Y-%m-%d", time.localtime(st.st_mtime))

    @staticmethod
    def link(chart, category):
        return f"<a href='/{category}/{chart}'>{chart}</a>"

    def chartlist(self):
        chartmix = copy.copy(self.charts)

        l_d = list()

        for ch in self.dupes:
            l_d.append(*ch.items())

        chartmix.update(l_d)

        s = "Follow the links to per-chart quality reports."
        s += "<br><br>"
        s += "<br>".join([self.link(chart, "charts") for chart in sorted(chartmix)])

        return s

    def maintainerlist(self):
        s = "Follow the links to per-maintainer consistency reports."
        s += "<br><br>"
        s += "<br>".join([self.link(maintainer, "maintainers") for maintainer in sorted(self.maintainers)])

        return s

    def frontpage(self):
        header = "HelmQA by Service Prototyping Lab, Zurich University of Applied Sciences"
        if self.configured:
            return header + "<br>" + self.chartlist() + "<br><br>" + self.maintainerlist()
        else:
            return "This instance is not configured to show analysis results. Presumably you want to use /livecheck programmatically, or run with -r for research mode?"

    def showchart(self, chart):
        s = ""

        list_dupes = list()

        for ch in self.dupes:
            list_dupes.append(*ch.keys())

        for cchart in list(self.charts.keys()) + list_dupes:
            if cchart.replace("-", "").startswith(chart) and cchart.replace("-", "") != chart:
                if s:
                    s += "<br>"

                s += self.showchart(cchart)

        if chart not in self.charts and chart not in list_dupes:
            if s:
                return s
            return "No such chart!"

        if s:
            s += "<br>"

        s += f"HelmQA advice on chart {chart} / data point {self.datapoint()}<br>"

        if chart in self.charts:
            for adv in self.charts[chart]:

                advbase = adv.split(":")[0]
                expl = "No explanation available."
                rat = None
                act = None

                if advbase == "multiple":
                    expl = "Two or more versions of the same chart appear in the same repository."
                    rat = "Developers may not understand which version to use."
                    act = "Unless there are compelling technical reasons, the advice is to stick to a single version " \
                          "per category and remove deprecated versions. "

                elif advbase == "equals":
                    expl = "The maintainer name equals a chart name."
                    rat = "This may be confusing to developers and may impede search and team maintenance."
                    act = "The advice is to change either the chart name or the maintainer name."

                elif advbase == "nomaint":
                    expl = "This chart does not have to be a maintainer entry."
                    rat = "In order to foster collaboration or feedback, each chart should have a contactable " \
                          "maintainer listed. "
                    act = "If you maintain this chart, the advice is to enter yourself as maintainer in the metadata."

                s += self.showbox(adv, expl, rat, act)

        if chart in list_dupes:
            adv = "duplicatevalues"
            expl = "The templates contain values with at least two duplicates which are candidates for template " \
                   "variable assignment. "
            rat = "Configuration duplication should be avoided. While false positives may occur, in some cases the " \
                  "detection points out potential consolidation of values in variables. "
            act = "Review the list (and if available, the suggested diff) to decide which duplicates should be " \
                  "removed in favour of variable assignments. Modify the chart templates accordingly. "
            act += "<br>The following occurrences of duplicate values have been found. Each entry consists of the " \
                   "value and the number of occurrences.<br> "
            act += str(self.dupes[list_dupes.index(chart)][chart])

            chartname = chart.replace(".tgz", "")
            diff = f"_diffs/{chartname}-deduplicated.diff"

            if os.path.isfile(diff):
                act += f"<br><a href='{diff}'>diff sketch available</a>"

            s += self.showbox(adv, expl, rat, act)

        return s

    def showmaintainer(self, maintainer):
        if maintainer not in self.maintainers:
            return "No such maintainer!"

        s = f"HelmQA advice on maintainer {maintainer} / data point {self.datapoint()}<br>"

        for adv in self.maintainers[maintainer]:

            advbase = adv.split(":")[0]
            expl = "No explanation available."
            rat = None
            act = None

            if advbase == "same":
                expl = "Two or more maintainer names across charts share the same e-mail address."
                rat = "This may be confusing to developers and may violate future cardinality restrictions."
                act = "The advice is to consolidate a 1:1 mapping of unique e-mail address to unique username."

            elif advbase == "equals":
                expl = "The maintainer name equals a chart name."
                rat = "This may be confusing to developers and may impede search and team maintenance."
                act = "The advice is to change either the chart name or the maintainer name."

            s += self.showbox(adv, expl, rat, act)

        return s

    @staticmethod
    def showbox(adv, expl, rat, act):
        h = "<br><div style='border-color:#000000;border-style:solid;border-width:1px'>"
        h += "<b>Issue: " + adv + "</b><br>"
        h += "Explanation:"

        boxstyle = "border-color:#bbbbbb;border-style:solid;border-width:1px;color:#b07777;padding:2px;margin:2px;"

        h += "<br><div style='" + boxstyle + "'>"
        h += str(expl)
        h += "</div>"
        h += "Rationale:"
        h += "<br><div style='" + boxstyle + "'>"
        h += str(rat)
        h += "</div>"
        h += "Recommended action:"
        h += "<br><div style='" + boxstyle + "'>"
        h += str(act)
        h += "</div>"
        h += "</div>"

        return h

    @staticmethod
    def showdiff(diff):
        with open(f"_diffs/{diff}") as f:
            r = flask.make_response(f.read(), 200)
            r.headers["Content-type"] = "text/plain"

        return r


@app.route("/charts/_diffs/<diff>")
def api_diff(diff):
    return HelmQA().showdiff(diff)


@app.route("/charts/<chart>")
def api_chart(chart):
    return HelmQA().showchart(chart)


@app.route("/maintainers/<maintainer>")
def api_maintainer(maintainer):
    return HelmQA().showmaintainer(maintainer)


@app.route("/charts/")
def api_charts():
    return HelmQA().chartlist()


@app.route("/maintainers/")
def api_maintainers():
    return HelmQA().maintainerlist()


@app.route("/")
def api_frontpage():
    return HelmQA().frontpage()


@app.route("/livecheck", methods=['GET'])
def api_livecheck():
    domainpath = request.args.get('repo', default=1)

    repo_name = f"{domainpath.split('/')[-2]}" + "-" + f"{domainpath.split('/')[-1].split('.')[0]}" if "/" and ("https://github.com/" or ".git") in domainpath else domainpath

    try:
        while repo_name[0] == "-":
            repo_name = repo_name[1:]
    except IndexError:
        repo_name = domainpath

    process = clone(f"{domainpath}", repo_name)

    response = dict()

    if "exists" in process:
        if "Already" in pull(repo_name):

            with open(f"dupestats_{repo_name}.json") as f:
                dupes = json.load(f)

            with open(f"authorsets_{repo_name}_charts.json") as f:
                mults = json.load(f)

                list_mults = list()
                list_mults.append(mults) if mults else None

            #if not list_mults and not dupes:
            if not list_mults:
                response["status"] = "success"
                response["code"] = 200
            else:
                response["status"] = "fail"
                response["code"] = 200
                response["duplicates"] = dupes
                response["multiplicates"] = list_mults

            return jsonify(response)

    elif "fatal" in process:
        response["message"] = f"{domainpath} doesn't exist"
        response["code"] = 200

        return jsonify(response)

    run_livecheck(repo_name)

    with open(f"dupestats_{repo_name}.json") as f:
        dupes = json.load(f)

    with open(f"authorsets_{repo_name}_charts.json") as f:
        mults = json.load(f)
        list_mults = list()
        list_mults.append(mults) if mults else 1

    #if not list_mults and not dupes:
    if not list_mults:
        response["status"] = "success"
        response["code"] = 200
    else:
        response["status"] = "fail"
        response["code"] = 200
        response["duplicates"] = dupes
        response["multiplicates"] = list_mults

    return jsonify(response)


def pull(repo_name):
    process = subprocess.Popen(['git', f'--git-dir={repo_name}/.git', 'pull'], stdout=subprocess.PIPE)
    process = process.communicate()[0].decode('UTF-8')
    return process


def clone(domain_path, repo_name):
    process = subprocess.Popen(['git', 'clone', domain_path, repo_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = process.communicate()[1].decode('UTF-8')
    return process


def run_livecheck(repo_name):
    from bucket import Bucket
    from dupestats import DupeStats
    from authorset import AuthorSet
    from rewriter import rewritechart

    bucket = Bucket(path=repo_name, desc=f"{repo_name}-descriptors")
    bucket.extract()

    stat = DupeStats(path=repo_name, dump_file=f"dupestats_{repo_name}.json")
    stat.dupe_stats()

    authorSet = AuthorSet(chartdir=repo_name,
                          authorset_charts=f"authorsets_{repo_name}_charts.json",
                          authorset_maint=f"authorsets_{repo_name}_maint.json",
                          authorset_email=f"authorsets_{repo_name}_emails.json",
                          authorset_heatmap=f"authorsets_{repo_name}-heatmap.png",
                          authorset_dot=f"authorsets_{repo_name}.dot",
                          authorset_png=f"autorsets_{repo_name}.png",
                          authorset_pdf=f"authorsets_{repo_name}.pdf",
                          dupestats_charts=f"dupestats_{repo_name}.json")

    authorSet.preprocess()
    authorSet.process()
    authorSet.processproposals()
    # authorSet.heatmap()
    # authorSet.dot()


    #
    # charts = sorted(stat.get_charts())
    #
    # for chart in charts:
    #     dupeslist = stat.dupefinder(chart)
    #     rewritechart(chart, dupeslist)
