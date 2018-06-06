# Adapted and ported from: https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
# Using QtWebKit as alternative to Selenium etc.

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
from lxml import html
import time
import json

class Render(QWebEnginePage):
  def __init__(self, url):
    self.app = QApplication(sys.argv)
    self.links = []
    QWebEnginePage.__init__(self)
    self.loadFinished.connect(self.loadFinishedSlot)
    self.load(QUrl(url))
    self.app.exec_()
  
  def loadFinishedSlot(self, result):
    self.frame = self
    self.app.quit()
    self.quit = False
    print("initial load finished")

  def functor(self, result):
    formatted_result = str(result)
    tree = html.fromstring(formatted_result)
    self.links = tree.xpath('//a//@href')
    print("loaded", len(self.links), "links")
    self.quit = True

  def spin(self):
    counter = 0
    while len(self.links) < 10:
      time.sleep(0.2)
      result = self.frame.toHtml(self.functor)
      while not self.quit:
        QApplication.processEvents()
      self.quit = False
      counter += 1
      if counter == 100:
          print("giving up")
          return
    print("full load finished")

url = "https://hub.kubeapps.com/charts"

r = Render(url)
r.spin()

linkset = set([link for link in r.links if link.startswith("/charts") and len(link.split("/")) == 4])
print("reduced link set", len(linkset))
print(sorted(linkset))

f = open("_helmlinks.json", "w")
json.dump(sorted(linkset), f)
f.close()
