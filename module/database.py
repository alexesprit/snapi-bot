# database.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import time

from module import io

class DataBase:
	def __init__(self, path):
		self.path = path
		self.ctpath = "%s.db" % (path)

		self.base = io.load(self.path, {})		
		self.changes = io.load(self.ctpath, {})

		self.__contains__ = self.base.__contains__
		self.__iter__ = self.base.__iter__
		
		self.__len__ = self.base.__len__
		self.__getitem__ = self.base.__getitem__

		self.items = self.base.items
		self.keys = self.base.keys
		self.values = self.base.values

	def __setitem__(self, item, value):
		self.base[item] = value
		self.changes[item] = time.time()

	def __delitem__(self, item):
		del self.base[item]
		del self.changes[item]

	def clear(self):
		self.base = {}
		self.changes = {}

	def save(self):
		io.dump(self.path, self.base)
		io.dump(self.ctpath, self.changes)

	def getChangeTime(self, item):
		return self.changes[item]

	def updateChangeTime(self, item):
		self.changes[item] = time.time()
