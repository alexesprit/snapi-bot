# version.py
# Initial Copyright (C) 2010-2011 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import base64
import hashlib
import os
import platform

class VersionInfo:
	def __init__(self):
		osinfo = platform.uname()
		self.osname = u"%s %s" % (osinfo[0], osinfo[2])

		self.capsstr = "http://snapi-bot.googlecode.com/caps"
		self.appname = "Snapi-Snup"

		self.major = "0"
		self.minor = "1"
		self.revision = os.popen("svnversion -n").read()
		if not self.revision:
			self.revision = "0"
		self.version = u"%s.%s.%s" % (self.major, self.minor, self.revision)
		self.verhash = None
		
		self.identcat = "bot"
		self.identname = "snapi"
		self.identtype = "pc"

	def createFeaturesHash(self, features):
		fString = "<".join(features)
		string = u"%s/%s//%s<%s<" % (self.identcat, self.identtype, self.identname, fString)
		self.verhash = base64.b64encode(hashlib.sha1(string).digest())

	def getAppName(self):
		return self.appname

	def getCapsString(self):
		return self.capsstr

	def getIdentCat(self):
		return self.identcat

	def getIdentName(self):
		return self.identname

	def getIdentType(self):
		return self.identtype

	def getMajorVer(self):
		return self.major

	def getMinorVer(self):
		return self.minor

	def getRevision(self):
		return self.revision

	def getVerString(self):
		return self.version

	def getOSName(self):
		return self.osname

	def getFeaturesHash(self):
		return self.verhash
