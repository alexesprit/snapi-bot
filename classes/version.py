# version.py
# Initial Copyright (C) 2010 -Esprit-

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

MAJOR_VER = 0
MINOR_VER = 1

IDENTITY_CAT = "bot"
IDENTITY_NAME = "snapi"
IDENTITY_TYPE = "pc"

CAPS = "http://snapi-bot.googlecode.com/caps"
APP_NAME = "Snapi-Snup"

class VersionInfo:
	def __init__(self):
		osinfo = platform.uname()

		self.osname = u"%s %s" % (osinfo[0], osinfo[2])

		pipe = os.popen("svnversion")
		rawRev = pipe.read()
		pipe.close()

		if not rawRev:
			rawRev = 0

		self.version = u"%d.%d.%s" % (MAJOR_VER, MINOR_VER, rawRev)
		self.verhash = None

	def createFeaturesHash(self, features):
		fString = "<".join(features)
		string = u"%s/%s//%s<%s<" % (IDENTITY_TYPE, IDENTITY_CAT, IDENTITY_NAME, fString)
		self.verhash = base64.b64encode(hashlib.sha1(string).digest())

	def getVersion(self):
		return self.version

	def getOSName(self):
		return self.osname

	def getFeaturesHash(self):
		return self.verhash
