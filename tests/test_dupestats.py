import unittest

from helmqa.dupestats import DupeStats


class DupeStatsTest(unittest.TestCase):

    def test_dupestats_class(self):
        stat = DupeStats(path='appuio-charts', verbose=True)
        stat.dupe_stats()

        self.assertEqual(1, sum(stat.stats_values))
        self.assertEqual('http', stat.allhitlist[0]["value"])
