# coding: utf-8;

# database.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

'''
	Простая "база данных" для плагинов. Написана исключительно для того, 
	чтобы поддерживать базы в чистом состоянии.
'''

import os, time;
import __main__;

class DataBase:
	def __init__(self, path):
		__main__.createFile(path, '{}');
		__main__.createFile(path + '.db', '{}');
		self.base = eval(__main__.readFile(path));
		self.changes = eval(__main__.readFile(path + '.db'));
		self.path = path;
	
	def __contains__(self, key):
		return(key in self.base);
	
	def __iter__(self):
		for item in self.base:
			yield(item);
	
	def __getitem__(self, item):
		return(self.base[item]);

	def __setitem__(self, item, value):
		self.base[item] = value;
		self.changes[item] = time.time();
	
	def __delitem__(self, item):
		del(self.base[item]);
		del(self.changes[item]);		
	
	def items(self):
		return(self.base.items());
	
	def clear(self):
		self.base = {};
		self.changes = {};
	
	def save(self):
		__main__.writeFile(self.path, str(self.base));
		__main__.writeFile(self.path + '.db', str(self.changes));
		
	def isEmpty(self):
		return(not self.base);
		
	def getUpdateTime(self, key):
		return(self.changes.get(key));
