from bucket import Bucket
from dupestats import DupeStats
from authorset import AuthorSet
from rewriter import rewritechart

bucket = Bucket()
bucket.download()
bucket.extract()

stat = DupeStats()
stat.dupe_stats()

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
