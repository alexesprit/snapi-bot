# macros.py
# Modification Copyright (c) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import random
import re

from module import utils

MACROS_FILE = "macros.txt"
MACCESS_FILE = "macrosaccess.txt"

class ArgParser:
	def __init__(self):
		self.commands = {
			"rand": self._getRandom,
			"context": self._getContext
		}

	def parseArgs(self, me):
		i = 0
		m = self._getMap(me)
		args = [""] * max(m)
		while i < len(m):
			if m[i]:
				args[m[i]-1] += me[i]
			i += 1
		return args

	def proccess(self, cmd, source):
		command = cmd[0]
		args = cmd[1:]
		return self._execCommand(command, args, source)

	def _getRandom(self, args, context):
		try:
			f = int(args[0])
			t = int(args[1])
			return str(random.randrange(f, t))
		except ValueError:
			return ""

	def _getContext(self, args, context):
		name = args[0]
		if name == "conf":
			return context[0]
		elif name == "nick":
			return context[1]
		return ""

	def _execCommand(self, cmd, args, source):
		if cmd in self.commands:
			return self.commands[cmd](args, source)
		return ""

	def _charMap(self, x, i):
		if i["esc"]:
			i["esc"] = False
			return i["level"]
		elif x == "\\":
			i["esc"] = True
			return 0
		elif x == "%":
			i["state"] = "cmd_p"
			return 0
		elif x == "(":
			if i["state"] == "cmd_p":
				i["level"] += 1
				i["state"] = "args"
			return 0
		elif x == ")":
			if i["state"] == "args":
				i["state"] = "null"
			return 0
		else:
			if i["state"] == "args":
				return i["level"]
			else:
				i["state"] = "null"
				return 0

	def _getMap(self, inp):
		i = {"level": 0, "state": "null", "esc": False}
		return [self._charMap(x, i) for x in list(inp)]

class Macros:
	def __init__(self, path):
		self.gMacrosList = {}
		self.gAccessList = {}
		self.macrosList = {}
		self.accessList = {}

		self.path = path

		self.parser = ArgParser()

	def loadMacroses(self, conference=None):
		if conference:
			path = os.path.join(self.path, conference, MACROS_FILE)
			self.macrosList[conference] = eval(utils.readFile(path, "{}"))

			path = os.path.join(self.path, conference, MACCESS_FILE)
			self.accessList[conference] = eval(utils.readFile(path, "{}"))
		else:
			path = os.path.join(self.path, MACROS_FILE)
			self.gMacrosList = eval(utils.readFile(path, "{}"))

			path = os.path.join(self.path, MACCESS_FILE)
			self.gAccessList = eval(utils.readFile(path, "{}"))

	def saveMacroses(self, conference=None):
		if conference:
			path = os.path.join(self.path, conference, MACROS_FILE)
			utils.writeFile(path, str(self.macrosList[conference]))

			path = os.path.join(self.path, conference, MACCESS_FILE)
			utils.writeFile(path, str(self.accessList[conference]))
		else:
			path = os.path.join(self.path, MACROS_FILE)
			utils.writeFile(path, str(self.gMacrosList))

			path = os.path.join(self.path, MACCESS_FILE)
			utils.writeFile(path, str(self.gAccessList))

	def freeMacroses(self, conference):
		del self.macrosList[conference]

	def getMacrosList(self, conference=None):
		if conference:
			return self.macrosList[conference].keys()
		else:
			return self.gMacrosList.keys()

	def getMacros(self, macros, conference=None):
		if conference:
			return self.macrosList[conference][macros]
		else:
			return self.gMacrosList[macros]

	def getParsedMacros(self, macros, param, context, conference=None):
		if conference:
			rawbody = self.macrosList[conference][macros]
		else:
			rawbody = self.gMacrosList[macros]

		if param is None:
			param = ""
		if rawbody.count("$*"):
			rawbody = rawbody.replace("$*", param)
		else:
			args = param.split()
			arglen = len(args)

			for i, n in enumerate(re.findall("\$[0-9]+", rawbody)):
				if arglen == i:
					break
				rawbody = rawbody.replace(n, args[i])

		for i in self.parser.parseArgs(rawbody):
			cmd = [x.strip() for x in i.split(",")]
			res = self.parser.proccess(cmd, context)
			if res:
				rawbody = rawbody.replace("%%(%s)" % i, res)
		return rawbody

	def hasMacros(self, macros, conference=None):
		if conference:
			return macros in self.macrosList[conference]
		else:
			return macros in self.gMacrosList

	def getAccess(self, macros, conference=None):
		if conference:
			return self.accessList[conference].get(macros)
		else:
			return self.gAccessList[macros]

	def setAccess(self, macros, access, conference=None):
		if conference:
			self.accessList[conference][macros] = access
		else:
			self.gAccessList[macros] = access

	def addMacros(self, macros, param, access, conference=None):
		if conference:
			self.macrosList[conference][macros] = param
		else:
			self.gMacrosList[macros] = param
		self.setAccess(macros, access, conference)

	def delMacros(self, macros, conference=None):
		if conference:
			if macros in self.macrosList[conference]:
				del self.macrosList[conference][macros]
				del self.accessList[conference][macros]
		else:
			if macros in  self.gMacrosList:
				del self.gMacrosList[macros]
				del self.gAccessList[macros]
