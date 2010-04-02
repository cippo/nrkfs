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

__version__ = "0.2"

try:
	import fuse
	fuse.fuse_python_api = (0, 2)
except ImportError:
	print "Library 'fuse' not found."
	exit()

try:
	import nrk
except ImportError:
	print "Library 'not' not found."
	exit()

import fuse, stat, errno, time

root = None

def getNode(path):
	global root
	if not root:
		root = nrk.getRoot()
	node = root
	for p in path.split("/")[1:]:
		if p != "" and node:
			node = node.getChild(p)
	return node

class Stat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = time.time()
        self.st_mtime = time.time()
        self.st_ctime = time.time()

class NrkFS(fuse.Fuse):

	def getattr(self, path):
		st = Stat()
		node = getNode(path)
		if node.isCut():
			st.st_mode = stat.S_IFREG | 0444
			st.st_nlink = 1
			st.st_size = 1000
		elif node:
			st.st_mode = stat.S_IFDIR | 0555
			st.st_nlink = 3
		else:
			return -errno.ENOENT
		return st

	def readdir(self, path, offset):
		children = getNode(path).getChildren().keys()
		children.sort()
		for r in [".", ".."] + children:
			yield fuse.Direntry(str(r))

	def open(self, path, flags):
		node = getNode(path)
		if not node.isCut():
			return -errno.ENOENT

	def read(self, path, size, offset):
		node = getNode(path)
		if not node.isCut():
			return -errno.ENOENT

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

if __name__ == '__main__':
    server = NrkFS(version="%prog " + fuse.__version__,
		 usage=fuse.Fuse.fusage,
		 dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()
