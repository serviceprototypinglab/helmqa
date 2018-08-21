import xml.dom.minidom as xml_dom
import urllib.request
import urllib.error
import os
import subprocess


class Bucket:
    """Provides an easy way to download and extract helm charts"""

    url_stable = "https://kubernetes-charts.storage.googleapis.com/"
    url_incubator = "http://storage.googleapis.com/kubernetes-charts-incubator"
    path_charts = "_charts"
    path_descriptors = "_descriptors"

    def __init__(self, url: str = url_stable, path: str = path_charts, desc: str = path_descriptors):
        """
        :param url: points to the xml document that hosts the charts
        :param path: the path where the charts will be stored
        :param desc: the path where the charts will be extracted
        """
        self.url = url
        self.path = path
        self.descriptor = desc
        self.releases = {}

    def download(self):
        """Downloads helm charts from the specified url"""

        if os.path.isdir(self.path):
            print("read index (cached)")
            return

        next_marker = None

        while True:
            next_marker = self.download_partial(next_marker)
            if not next_marker:
                break

        self.write()

    def download_partial(self, marker=None):
        """
        Downloads the partial xml document and returns a pointer to the next document (if any).

        :param marker: pointer to the rest of the charts
        :return: next_marker if there's any, or None.
        """
        print(f'read index... [{marker}]')

        murl = self.url

        if marker:
            murl += f'?marker={marker}'

        with urllib.request.urlopen(murl) as req:
            res = req.read().decode("utf-8")

        dom = xml_dom.parseString(res)

        keys, next_marker = self.scan(dom)

        releases = self.get_releases(keys)

        self.releases = {**self.releases, **releases}

        os.makedirs(self.path, exist_ok=True)

        return next_marker

    def write(self):
        """
        Downloads each chart specified in the releases dictionary and stores them
        in the specified path.
        """
        for release in self.releases:
            rel = release + '-' + self.releases[release]
            dllink = self.url + rel

            print(f"-fetch", dllink, "...")

            with urllib.request.urlopen(dllink) as req:
                res = req.read()

            with open(os.path.join(self.path, rel), "wb") as f:
                f.write(res)

    def extract(self):
        """Extracts chart templates from packaged charts"""

        # if os.path.isdir(self.descriptor):
        #     print("render templates (cached)")
        #     return

        print("render templates...")

        charts = os.listdir(self.path)

        os.makedirs(self.descriptor, exist_ok=True)

        for chart in charts:
            if chart.endswith(".tgz"):

                chart_name = os.path.join(self.path, chart)

                p = subprocess.run(f"helm template {chart_name}", shell=True, stdout=subprocess.PIPE)

                yaml = os.path.join(self.descriptor, chart.replace(".tgz", ".yaml"))

                with open(yaml, "wb") as f:
                    f.write(p.stdout)

    @staticmethod
    def get_releases(keys):
        """
        Takes in the keys list and returns a dictionary [str: str].
        The chart's name is the key, and the version is the value.
        If multiple versions of the same chart are included,
        only the latest version is added to the dictionary.

        :param keys: List of charts from the chart repository
        :return: releases dict
        """
        releases = {}

        for key in keys:
            parts = key.split("-")
            basename = "-".join(parts[:-1])
            version = parts[-1]

            if not basename:
                continue

            if basename not in releases:
                releases[basename] = version

            elif version > releases[basename]:
                releases[basename] = version

        return releases

    @staticmethod
    def scan(dom):
        """
        Takes the dom of the xml and scans for the "Key" and "NextMarker" elements.
        - Key contains the chart's name and version.
        - NextMarker points to the next document.

        We need NextMarker to retrieve the remaining charts because the xml document
        is truncated.

        The value of Key is appended to the keys list and returned when the dom is consumed.
        The value of NextMarker is returned as well, so the rest of the charts can be retrieved.

        :param dom: dom parsed from the url containing charts
        :return: keys list, next_marker.
        """
        keys = []
        next_marker = None

        for element in dom.childNodes:
            for element2 in element.childNodes:
                if element2.nodeName == "Contents":
                    for element3 in element2.childNodes:
                        if element3.nodeName == "Key":
                            keys.append(element3.childNodes[0].nodeValue)
                elif element2.nodeName == "NextMarker":
                    next_marker = element2.childNodes[0].nodeValue

        return keys, next_marker
