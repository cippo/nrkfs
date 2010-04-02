# -*- coding: utf-8 -*-

# This file is part of NrkFS.
#
# NrkFS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# NrkFS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NrkFS. If not, see <http://www.gnu.org/licenses/>.

__version__ = "0.1a3"

from BeautifulSoup import BeautifulSoup 
import urllib2, time, re

switchDate = re.compile("(.*)( )([0-9]{2})\.([0-9]{2})\.[0-9]{0,2}([0-9]{2})(.*)")

class Node():
	def __init__(self, title, href):
		self.children = dict()
		self.title = title
		self.href = href
		self.cut = None
		self.updated = time.time()
		
		d = switchDate.match(self.title)
		if d:
			n = d.groups()
			self.title = n[4] + "-" + n[3] + "-" + n[2] + " " + n[0] + n[5]

	def addChildren(self, children):
		self.updated = time.time()
		self.children = dict()
		for c in children:
			node = Node(c[0], c[1])
			if node.isCut():
				self.children[node.title + ".asx"] = node
			else:
				self.children[node.title] = node

	def getChildren(self):
		if len(self.children) == 0 or self.updated + 120 < time.time():
			if self.isTheme():
				self.addChildren(getTheme(self.href))
			elif self.isProject():
				self.addChildren(getProject(self.href))
			elif self.isCategory():
				self.addChildren(getCategory(self.href))

		return self.children
	
	def getChild(self, title):
		self.getChildren()
		if self.getChildren().has_key(title):
			return self.getChildren()[title]
		else:
			return None
			
	def isTheme(self):
		return self.href.count("tema") > 0
	
	def isProject(self):
		return self.href.count("prosjekt") > 0
		
	def isCategory(self):
		return self.href.count("kategori") > 0
		
	def isCut(self):
		return self.href.count("klipp") > 0
	
	def getCut(self):
		if self.isCut():
			if not self.cut:
				self.cut = getCut(self.href)
			return self.cut
	
	def __repr__(self):
		return self.title
		
def getRoot():
	root = Node("root", "/")
	root.addChildren(getThemes())
	root.updated = time.time() * 2

	return root

def request(url, split = None):
	if url[0] == "/":
		url = "http://www1.nrk.no" + url
	cookie = """NetTV2.0Speed=NetTV2.0Speed=10530; UseSilverlight=UseSilverlight=0;"""
	req = urllib2.Request(url, None, {'Cookie': cookie})
	res = urllib2.urlopen(req)
	if split:
		soup = BeautifulSoup(res.read().split(split)[1])
	else:
		soup = BeautifulSoup(res.read())
	res.close()
	return soup

def getThemes():
	ul = request("http://www1.nrk.no/nett-tv/").findAll(id="categories")[0]
	return [(b["title"].encode("utf8").split("'")[1], b["href"]) for b in ul.findAll("a")]

def getTheme(url):
	ret = []
	ul = request(url, "nettv-category")
	for a in ul.findAll("li"):
		if a.find("div"):
			a = a.find("a")
		# el = a.find("h2").find("a")
			ret.append((a["title"].split(" - ")[0].encode("utf8"), a["href"]))
	return ret

def getProject(url):
	ret = []
	ul = request(url)
	ul = ul.find(id= "ctl00_ucContent_menu")
	for a in ul.findAll("li"):
		try:
			el = a.find("a")
			ret.append((el["title"].encode("utf8"), el["href"]))
		except:
			pass
	return ret

def getCategory(url):
	ret = []
	ul = request(url)
	# ul = ul.findAll("ul", {"class": "icon-video-black"})[-1]
	for a in ul.findAll("a", {"class": "icon-video-black"}):
		# Should use a.string, not a[title]
		ret.append((a["title"].encode("utf8"), a["href"]))
	return ret

def getCut(url):
	print url
	ul = request(url)
	url = None
	for p in ul.findAll("param"):
		if p["name"] == "Url":
			 url = p["value"]
			 break
	for p in request(url).findAll("ref"):
		if p["href"][0:3] == "mms":
			return p["href"]

// print getRoot().getChild("Nyheter").getChild("Dagsrevyen").getChild("Mars 10").getChild("10-03-09 Dagsrevyen.asx").getCut()
