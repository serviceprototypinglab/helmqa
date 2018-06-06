url_stable = "https://kubernetes-charts.storage.googleapis.com/"
url_incubator = "http://storage.googleapis.com/kubernetes-charts-incubator"
path_charts = "_charts"
path_descriptors = "_descriptors"

url = url_stable

import xml.dom.minidom
import urllib.request
import os
import subprocess

def downloadpartial(url, path, marker=None):
	print("read index... [{}]".format(marker))
	murl = url
	if marker:
		murl += "?marker={}".format(marker)
	req = urllib.request.urlopen(murl)
	res = req.read().decode("utf-8")

	keys = []
	nextmarker = None

	dom = xml.dom.minidom.parseString(res)
	for element in dom.childNodes:
		for element2 in element.childNodes:
			if element2.nodeName == "Contents":
				for element3 in element2.childNodes:
					if element3.nodeName == "Key":
						keys.append(element3.childNodes[0].nodeValue)
			elif element2.nodeName == "NextMarker":
				nextmarker = element2.childNodes[0].nodeValue

	releases = {}
	for key in keys:
		parts = key.split("-")
		basename = "-".join(parts[:-1])
		version = parts[-1]
		if not basename:
			continue
		#print(basename, version)
		if not basename in releases:
			#print("enter", basename)
			releases[basename] = version
		elif version > releases[basename]:
			#print("upgrade", basename)
			releases[basename] = version

	os.makedirs(path, exist_ok=True)
	for release in releases:
		rel = release + "-" + releases[release]
		dllink = url + rel
		print("fetch", dllink, "...")
		req = urllib.request.urlopen(dllink)
		res = req.read()
		f = open(os.path.join(path, rel), "wb")
		f.write(res)
		f.close()

	return nextmarker

def download(url, path):
	if os.path.isdir(path):
		print("read index (cached)")
		return

	nextmarker = None
	while True:
		nextmarker = downloadpartial(url, path, nextmarker)
		if not nextmarker:
			break

def extract(path, descriptorpath):
	if os.path.isdir(path_descriptors):
		print("render templates (cached)")
		return
	print("render templates...")
	charts = os.listdir(path)
	os.makedirs(descriptorpath, exist_ok=True)
	for chart in charts:
		if chart.endswith(".tgz"):
			p = subprocess.run("helm template {}".format(os.path.join(path, chart)), shell=True, stdout=subprocess.PIPE)
			f = open(os.path.join(descriptorpath, chart.replace(".tgz", ".yaml")), "wb")
			f.write(p.stdout)
			f.close()

download(url, path_charts)
extract(path_charts, path_descriptors)
