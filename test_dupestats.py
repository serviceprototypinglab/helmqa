import unittest

from dupestats import DupeStats


class DupeStatsTest(unittest.TestCase):

    def test_dupestats_class(self):
        stat = DupeStats(path='.test_charts/', verbose=True)
        stat.dupe_stats()

        self.assertEqual(1, sum(stat.stats_values))
        self.assertEqual('http', stat.allhitlist[0][0])
