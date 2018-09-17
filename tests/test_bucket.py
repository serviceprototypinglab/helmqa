import unittest
from helmqa.bucket import Bucket
import xml.dom.minidom as xml_dom
import os


class BucketTest(unittest.TestCase):

    def setUp(self):
        self.bucket = Bucket()

    def test_scan(self):
        """
        Test for the scan method
        :return:
        """
        dom = '<ListBucketResult xmlns="http://doc.s3.amazonaws.com/2006-03-01"><Name>kubernetes-charts</Name><Prefix' \
              '/><Marker/><NextMarker>kapacitor-0.3.0.tgz</NextMarker><IsTruncated>true</IsTruncated><Contents><Key' \
              '>acs-engine-autoscaler-0.1.0.tgz</Key><Generation>1501637633913843</Generation><MetaGeneration>1' \
              '</MetaGeneration><LastModified>2017-08-02T01:33:53.600Z</LastModified><ETag' \
              '>"7ba1dd9555e78f23eac07a7223cdad18"</ETag><Size>4069</Size></Contents><Contents><Key>acs-engine' \
              '-autoscaler-1.0.0.tgz</Key><Generation>1505061247273212</Generation><MetaGeneration>1</MetaGeneration' \
              '><LastModified>2017-09-10T16:34:07.187Z</LastModified><ETag>"fcea91b52795fb8576be7a62ceebb731"</ETag' \
              '><Size>4229</Size></Contents></ListBucketResult>'

        dom = xml_dom.parseString(dom)
        keys, next_marker = self.bucket.scan(dom)

        valid_keys = ['acs-engine-autoscaler-0.1.0.tgz', 'acs-engine-autoscaler-1.0.0.tgz']
        valid_next_marker = 'kapacitor-0.3.0.tgz'

        self.assertEqual(keys, valid_keys)
        self.assertEqual(next_marker, valid_next_marker)

    def test_get_releases(self):
        """
        Test for the get_releases method.
        :return:
        """
        diff_rel = ['acs-engine-autoscaler-0.1.0.tgz', 'artifactory-ha-0.1.7.tgz']
        same_rel = ['acs-engine-autoscaler-0.1.0.tgz', 'acs-engine-autoscaler-1.0.0.tgz']

        valid_diff_rel = {'acs-engine-autoscaler': '0.1.0.tgz', 'artifactory-ha': '0.1.7.tgz'}
        valid_same_rel = {'acs-engine-autoscaler': '1.0.0.tgz'}

        diff_releases = self.bucket.get_releases(diff_rel)
        same_releases = self.bucket.get_releases(same_rel)

        self.assertEqual(same_releases, valid_same_rel)
        self.assertEqual(diff_releases, valid_diff_rel)

    def test_bucket_class(self):
        """
        Test for the Bucket class.
        At the moment, it'll only work if the _charts and _descriptor directories don't exist.
        :return:
        """
        self.bucket.download()
        self.bucket.extract()

        chart_count = len(os.listdir(self.bucket.path))
        template_count = len(os.listdir(self.bucket.descriptor))
        releases_count = len(self.bucket.releases)

        print(f"chart_count: {chart_count}")
        print(f"template_count: {template_count}")
        print(f"releases_count: {releases_count}")

        self.assertEqual(chart_count, template_count)
        self.assertEqual(chart_count or template_count, releases_count)

