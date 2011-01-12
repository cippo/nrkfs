#!/usr/bin/env python
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
	import fuse
	fuse.fuse_python_api = (0, 2)
except ImportError:
	print "Library 'fuse' not found."
	exit()

try:
	import nrk
except ImportError:
	print "Library 'nrk' not found."
	exit()

import fuse, stat, errno, time, os, sys, getopt

root = None
config = {}
logfile = None

def log(*txt):
	global logfile
	if logfile != None:
		logfile.write(" ".join([str(x) for x in txt]) + "\n")
		logfile.flush()

def getNode(path):
	global root
	if not root:
		root = nrk.getRoot()

	node = root
	for p in path.split("/")[1:]:
		if p.strip() != "" and node != None:
			node = node.getChild(p)
	
	return node

class Stat(fuse.Stat):
    def __init__(self):

        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = os.getuid()
        self.st_gid = os.getgid()
        self.st_size = 4096

class NrkFS(fuse.Fuse):

	def getattr(self, path):
		log("getattr", path)

		if path in ["/.Trash", "/.Trash-1000"]:
			log("-", "No such file or directory")
			return errno.ENOENT

		node = getNode(path)

		if node == None:
			log("-", "No such file or directory")
			return -errno.ENOENT

		st = Stat()
		st.st_atime = int(node.updated)
		st.st_mtime = int(node.updated)
		st.st_ctime = int(node.updated)

		if node.isFile():
			st.st_mode = stat.S_IFREG | 0444
			st.st_nlink = 1
			st.st_size = 1000
		else:
			st.st_mode = stat.S_IFDIR | 0555
			st.st_nlink = 3
		return st

	def readdir(self, path, offset):
		log("readdir", path, offset)

		children = getNode(path).getChildren().keys()
		children.sort()
		for r in [".", ".."] + children:
			yield fuse.Direntry(str(r))

	def open(self, path, flags):
		log("open", path, flags)

		node = getNode(path)
		if not node.isFile():
			return -errno.ENOENT

	def read(self, path, size, offset):
		log("read", path, offset)

		node = getNode(path)

		if not node.isFile():
			return -errno.ENOENT

		#if node.isCut():

		playlist = """
<?xml version="1.0" encoding="UTF-8"?>
<asx version="3.0">
  <title>NRK Nett-TV</title>
  <author>NRK - Norsk Rikskringkasting</author>
  <entry>
    <title>%s</title>
    <ref href="%s" />
  </entry>
</asx>""" % (node.title, str(node.getCut()))

		#elif node.isDirectTv():
		#	playlist = node.title

		playlist += " " * (1000 - len(playlist))

		# Good help from hello.py in the FUSE project
		slen = len(playlist)
		if offset < slen:
			if offset + size > slen:
				size = slen - offset
			buf = playlist[offset:offset+size]
		else:
			buf = ''
		return buf

def main():
	#optlist, sys.argv = getopt.getopt(sys.argv, 'b:c:l:o:')

	#for ok, ov in optlist:
	#	if ok == "-o":
	#		sys.argv.append(ok + ov)
	#	elif ok[1:] in ["b", "c"]:
	#		nrk.config[ok[1:]] = int(ov)
	#	else:
	#		config[ok[1:]] = ov

	#if config.has_key("l"):
	#	logfile = open(config["l"], "w")
	#	log("Starting...")

	server = NrkFS(version="%prog " + fuse.__version__,
			usage=fuse.Fuse.fusage,
			dash_s_do='setsingle')

	server.parse(errex=1)
	try:
		server.main()
	except Exception, e:
		print str(e)
		log(e)

if __name__ == '__main__':
	main()
