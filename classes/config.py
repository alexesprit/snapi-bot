# coding: utf-8

# config.py
# Initial Copyright (C) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

class Config:
	def __init__(self, path):
		execfile(path, self.__dict__)

		self.USERNAME, self.SERVER = self.JID.split("@")