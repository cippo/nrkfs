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

__version__ = "0.4.0"

try:
	import nrk
except ImportError:
	print "Library 'nrk' not found."
	exit()

import os, os.path, sys

playlist = """<?xml version="1.0" encoding="UTF-8"?>
<asx version="3.0">
  <title>NRK Nett-TV</title>
  <author>NRK - Norsk Rikskringkasting</author>
  <entry>
    <title>%s</title>
    <ref href="%s" />
  </entry>
</asx>"""


def read(node, name):
	if node.isFile():
		if len(name) > 255:
			name = name[0:250] + ".asx"
		if not os.path.exists(name) or os.path.getsize(name) == 0:
			f = open(name, "w")
			try:
				output = playlist % (node.title, str(node.getCut().encode("utf-8")))
				f.write(output)
			except Exception, e:
				print name, e
			f.close()
	else:
		print name
		if not os.path.exists(name):
			os.mkdir(name)
		children = node.getChildren()
		for n in children:
			read(children[n], name + "/" + n)

if __name__ == '__main__':
	folder = "nrk"
	if len(sys.argv) == 2:
		folder = sys.argv[1]
	read(nrk.getRoot(), folder.rstrip("/"))
