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

__version__ = "0.3.3"

try:
	from BeautifulSoup import BeautifulSoup 
except ImportError:
	print "Library 'BeauitifulSoup' not found."
	exit()

import urllib2, time, re

switchDate = re.compile("(.*)( )([0-9]{2})\.([0-9]{2})\.[0-9]{0,2}([0-9]{2})(.*)")

config = dict(b=10000, c=120)

class Node:
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
		for c in children:
			node = Node(c[0], c[1])
			if node.isCut() or node.isDirectTv():
				self.children[node.title + ".asx"] = node
			else:
				self.children[node.title] = node

	def getChildren(self):
		global config

		if len(self.children) == 0 or self.updated + config["c"] < time.time():
			self.children = dict()
			if self.isTheme():
				self.addChildren(getTheme(self.href))
			elif self.isProject():
				self.addChildren(getProject(self.href))
			elif self.isCategory():
				self.addChildren(getCategory(self.href))
			elif self.isDirect():
				self.addChildren(getDirect())

		return self.children
	
	def getChild(self, title):
		self.getChildren()
		if self.getChildren().has_key(title):
			return self.getChildren()[title]
		else:
			return None

	def isFile(self):
		return self.isCut() or self.isDirectTv()

	def isTheme(self):
		return self.href.count("tema") > 0
	
	def isProject(self):
		return self.href.count("prosjekt") > 0
		
	def isCategory(self):
		return self.href.count("kategori") > 0
		
	def isCut(self):
		return self.href.count("klipp") > 0
		
	def isDirect(self):
		return self.href == "direkte"
		
	def isDirectTv(self):
		return self.href.count("direkte/") > 0
	
	def getCut(self):
		if self.isFile():
			if self.isCut() or self.isDirectTv():
				if not self.cut:
					self.cut = getCut(self.href)
				return self.cut
	
	def __repr__(self):
		return self.title
		
def getRoot():
	root = Node("root", "/")
	root.addChildren(getThemes())
	root.addChildren([("Direkte", "direkte")])
	root.updated = time.time()

	return root

def fixName(name):
	return name.encode("utf8").strip().replace("/", "-")

def request(url, split = None):
	global config

	if url[0] == "/":
		url = "http://www1.nrk.no" + url
	cookie = """NetTV2.0Speed=NetTV2.0Speed=""" + str(config["b"]) + """; UseSilverlight=UseSilverlight=0;"""
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
	return [(fixName(b["title"].split("'")[1]), b["href"]) for b in ul.findAll("a")]

def getTheme(url):
	ret = []
	ul = request(url, "nettv-category")
	for a in ul.findAll("li"):
		if a.find("div"):
			a = a.find("a")
			ret.append((fixName(a["title"].split(" - ")[0]), a["href"]))
	return ret

def getProject(url):
	ret = []
	ul = request(url)
	ul = ul.find(id= "ctl00_contentPlaceHolder_UcProjectInfo_menu")
	for a in ul.findAll("li"):
		try:
			el = a.find("a")
			ret.append((fixName(el["title"]), el["href"]))
		except:
			pass
	return ret

def getCategory(url):
	try:
		ret = []
		ul = request(url)
		ul = ul.find("ul", {"id": "folder" + url.split("/")[-1]})
		for a in ul.findAll("a"):
			if a.string != "&nbsp;":
				ret.append((fixName(unicode(a.string)), a["href"]))
		return ret
	except Exception, e:
		return []

def getCut(url):
	ul = request(url)
	url = None
	for p in ul.findAll("param"):
		if p["name"] == "Url":
			 url = p["value"]
			 break
	for p in request(url).findAll("ref"):
		if p["href"][0:3] == "mms":
			return p["href"]
			
def getDirect():
	ret = []
	ul = request("http://www.nrk.no/nett-tv/direkte/", "live-channels")
	for p in ul.find("ul").findAll("li"):
		p = p.find("h3").find("a")
		if p:
			ret.append((fixName(p["title"]), "http://www.nrk.no" + p["href"]))
	return ret
