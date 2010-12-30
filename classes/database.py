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

from utils import utils

class DataBase:
	def __init__(self, path):
		self.path = path		
		utils.createFile(self.path, "{}")
		self.base = eval(utils.readFile(self.path))

		self.ctpath = "%s.db" % (path)
		utils.createFile(self.ctpath, "{}")
		self.changes = eval(utils.readFile(self.ctpath))
	
	def __nonzero__(self):
		if self.base:
			return 1
		return 0

	def __contains__(self, item):
		return item in self.base
	
	def __iter__(self):
		for item in self.base:
			yield item
	
	def __getitem__(self, item):
		return self.base[item]

	def __setitem__(self, item, value):
		self.base[item] = value
		self.changes[item] = time.time()
	
	def __delitem__(self, item):
		del self.base[item]
		del self.changes[item]

	def keys(self):
		return self.base.keys()

	def values(self):
		return self.base.values()

	def items(self):
		return self.base.items()
	
	def clear(self):
		self.base = {}
		self.changes = {}
	
	def save(self):
		utils.writeFile(self.path, str(self.base))
		utils.writeFile(self.ctpath, str(self.changes))
		
	def getChangeTime(self, item):
		return self.changes[item]
		
	def updateChangeTime(self, item):
		self.changes[item] = time.time()
