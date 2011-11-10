# debug.py 

# Copyright (c) 2003 Jacob Lundqvist

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

_version_ = '1.4.0'

"""
	Generic debug class

	Other modules can always define extra debug flags for local usage, as long as
	they make sure they append them to debugFlags

	Also its always a good thing to prefix local flags with something, to reduce risk
	of coliding flags. Nothing breaks if two flags would be identical, but it might 
	activate unintended debugging.

	flags can be numeric, but that makes analysing harder, on creation its
	not obvious what is activated, and when flag_show is given, output isnt
	really meaningfull.

	This Debug class can either be initialized and used on app level, or used independantly
	by the individual classes.

	For samples of usage, see samples subdir in distro source, and selftest
	in this code
"""

import os
import sys
import time
import traceback

useColors = ("TERM" in os.environ)

colorNone			= chr(27) + "[0m"
colorBlack			= chr(27) + "[30m"
colorRed			= chr(27) + "[31m"
colorGreen			= chr(27) + "[32m"
colorBrown			= chr(27) + "[33m"
colorBlue			= chr(27) + "[34m"
colorMagenta		= chr(27) + "[35m"
colorCyan			= chr(27) + "[36m"
colorLightGray		= chr(27) + "[37m"
colorDarkGray		= chr(27) + "[30;1m"
colorBrightRed		= chr(27) + "[31;1m"
colorBrightGreen	= chr(27) + "[32;1m"
colorYellow			= chr(27) + "[33;1m"
colorBrightBlue		= chr(27) + "[34;1m"
colorPurple			= chr(27) + "[35;1m"
colorBrightCyan		= chr(27) + "[36;1m"
colorWhite			= chr(27) + "[37;1m"

"""
	Define your flags in yor modules like this:

		from debug import Debug

		DBG_INIT = "init"
		DBG_CONNECTION = "connection"
		dbgFlags = (DBG_INIT, DBG_CONNECTION)

	The reason for having a double statement wis so we can validate params
	and catch all undefined debug flags

	This gives us control over all used flags, and makes it easier to allow
	global debugging in your code, just do something like

		foo = Debug(dbgFlags)

	---

	NoDebug

	To speed code up, typically for product releases or such
	use this class instead if you globaly want to disable debugging
"""

DBG_ALWAYS = "always"

class NoDebug:
	def __init__(self, *args, **kwargs):
		self.colors = {}
		self.debugFlags = []

	def show(self,  *args, **kwargs):
		pass

	def isActive(self, flag):
		pass

	def setActiveFlags(self, activeFlags=None):
		return 0

class Debug:  
	colors = {}
    
	def __init__(self, activeFlags=None, logFile=sys.stderr, 
				prefix="", suffix="\n", timeStamp=0,
				showFlags=True, validateFlags=False, welcomeMsg=False):
		"""
			prefix and suffix:
				prefix and sufix can either be set globaly or per call.
				personally I use this to color code debug statements
				with prefix = chr(27) + "[34m"
					 suffix = chr(27) + "[37;1m\n"
			
			timeStamp:
				0 - disables timestamps
				1 - before prefix, good when prefix is a string
				2 - after prefix, good when prefix is a color
		
		"""
		if isinstance(activeFlags, tuple) or isinstance(activeFlags, list):
			self.debugFlags = activeFlags
		else:
			raise TypeError("activeFlags must be list or tuple!")
		if welcomeMsg:
			welcomeMsg = activeFlags and 1 or 0
		if logFile:
			if isinstance(logFile, str):
				try:
					self._fh = open(logFile, "w")
				except IOError:
					raise IOError("Unable to open %s for writing" % (logFile))
					sys.exit(0)
			else:
				self._fh = logFile
		else:
			self._fh = sys.stdout
		
		if timeStamp not in (0, 1, 2):
			raise TypeError("Invalid timeStamp param", timeStamp)
		self.prefix = prefix
		self.suffix = suffix
		self.timeStamp = timeStamp
		self.validateFlags = validateFlags
		self.showFlags = showFlags
		self.colors = {}

		self.setActiveFlags(activeFlags)
		if welcomeMsg:
			caller = sys._getframe(1)
			try:
				modName = ":%s" % (caller.f_locals["__name__"])
			except NameError:
				modName = ""
			self.show("Debug created for %s%s" % (caller.f_code.co_filename, modName))
			self.show("Flags defined: %s" % ", ".join(self.activeFlags))

	def setActiveFlags(self, activeFlags=None):
		validFlags = []
		if not activeFlags:
			self.activeFlags = []
			return
		elif isinstance(activeFlags, tuple) or isinstance(activeFlags, list):
			for flag in activeFlags:
				self._validateFlag(flag)
				validFlags.append(flag)
			self.activeFlags = validFlags
			self._removeDuplicates()
		else:
			raise TypeError("activeFlags must be list or tuple!")

	def getActiveFlags(self):
		return self.activeFlags

	def show(self, msg, flag=None, prefix=None):
		if flag and self.validateFlags:
			self._validateFlag(flag)
		if not flag or self.isActive(flag):
			if not isinstance(msg, basestring):
				msg = unicode(msg)
			prefixColor = ""
			if useColors and prefix in self.colors:
				prefixColor = self.colors[prefix]
				msg = prefixColor + msg + colorNone
				if flag:
					flagColor = self.colors[flag]
			if prefix == "error":
				if sys.exc_info()[0]:
					msg += "\n" + traceback.format_exc().rstrip()
			prefix = self.prefix
			if self.showFlags and flag:
				prefix += "%s[%s]%s " % (flagColor, flag, colorNone)
			if self.timeStamp == 2:
				prefix = "%s%s " % (prefix, time.strftime("[%H:%M:%S]"))
			elif self.timeStamp == 1:
				prefix = "%s %s" % (time.strftime("[%H:%M:%S]"), prefix)
			output = "%s%s%s" % (prefix, msg, self.suffix)
			if isinstance(output, unicode):
				if "posix" == os.name:
					output = output.encode("utf-8")
				elif "nt" == os.name:
					output = output.encode("cp866")
			self._fh.write(output)
			self._fh.flush()

	def isActive(self, flag):
		if self.activeFlags: 
			if not flag or flag in self.activeFlags or DBG_ALWAYS in self.activeFlags:
				return True
		return False

	def _validateFlag(self, flag):
		if flag and not flag in self.debugFlags:
			raise KeyError("Invalid debug flag given: %s" % flag)

	def _removeDuplicates(self):
		self.debugFlags = list(set(self.debugFlags))
