from bucket import Bucket
from dupestats import DupeStats
from authorset import AuthorSet
from rewriter import rewritechart
import os

if os.path.isdir("/charts"):
       os.chdir("/charts")
       bucket = Bucket(path="/charts")
else:
       bucket = Bucket()
bucket.download()
bucket.extract()

if os.path.isdir("/charts"):
    stat = DupeStats(path="/charts")
else:
    stat = DupeStats()
stat.dupe_stats()

if os.path.isdir("/charts"):
    authorSet = AuthorSet(chartdir="/charts")
else:
    authorSet = AuthorSet()
authorSet.preprocess()
authorSet.process()
authorSet.processproposals()
authorSet.heatmap()
authorSet.dot()

charts = sorted(stat.get_charts())

for chart in charts:
    dupeslist = stat.dupefinder(chart)
    rewritechart(chart, dupeslist)
