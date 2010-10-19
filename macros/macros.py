# coding: utf-8

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

import utils.utils as util

MACROS_FILE = 'macros.txt'
MACCESS_FILE = 'macrosaccess.txt'

class Macros:
	def __init__(self, path):
		self.commands = {
			'rand': self.getRand,
			'context': self.getContext
		}
		self.gMacrosList = {}
		self.gAccessList = {}
		self.macrosList = {}
		self.accessList = {}
		self.path = path

	def loadMacroses(self, conference=None):
		if(conference):
			macrosFileName = util.getFilePath(self.path, conference, MACROS_FILE)
			accessFileName = util.getFilePath(self.path, conference, MACCESS_FILE)
			
			util.createFile(macrosFileName, '{}')
			util.createFile(accessFileName, '{}')

			self.macrosList[conference] = eval(util.readFile(macrosFileName))
			self.accessList[conference] = eval(util.readFile(accessFileName))
		else:
			macrosFileName = util.getFilePath(self.path, MACROS_FILE)
			accessFileName = util.getFilePath(self.path, MACCESS_FILE)

			util.createFile(macrosFileName, '{}')
			util.createFile(accessFileName, '{}')

			self.gMacrosList = eval(util.readFile(macrosFileName))
			self.gAccessList = eval(util.readFile(accessFileName))

	def saveMacroses(self, conference=None):
		if(conference):
			macrosFileName = util.getFilePath(self.path, conference, MACROS_FILE)
			accessFileName = util.getFilePath(self.path, conference, MACCESS_FILE)
			util.writeFile(macrosFileName, str(self.macrosList[conference]))
			util.writeFile(accessFileName, str(self.accessList[conference]))
		else:
			macrosFileName = util.getFilePath(self.path, MACROS_FILE)
			accessFileName = util.getFilePath(self.path, MACCESS_FILE)
			util.writeFile(macrosFileName, str(self.gMacrosList))
			util.writeFile(accessFileName, str(self.gAccessList))
			
	def freeMacroses(self, conference):
		if(conference in self.macrosList):
			del(self.macrosList[conference])

	def getMacrosList(self, conference=None):
		if(conference):
			return(self.macrosList[conference].keys())
		else:
			return(self.gMacrosList.keys())

	def getMacros(self, macros, conference=None):
		if(conference):
			return(self.macrosList[conference].get(macros))
		else:
			return(self.gMacrosList.get(macros))
		
	def hasMacros(self, macros, conference = None):
		if(conference):
			return(macros in self.macrosList[conference])
		else:
			return(macros in self.gMacrosList)
			
	def getAccess(self, macros, conference=None):
		if(conference):
			return(self.accessList[conference].get(macros))
		else:
			return(self.gAccessList[macros])

	def setAccess(self, macros, access, conference=None):
		if(conference):
			self.accessList[conference][macros] = access
		else:
			self.gAccessList[macros] = access

	def add(self, macros, param, access, conference=None):
		if(conference):
			self.macrosList[conference][macros] = param
		else:
			self.gMacrosList[macros] = param
		self.setAccess(macros, access, conference)

	def remove(self, macros, conference=None):
		if(conference):
			if(macros in self.macrosList[conference]):
				del(self.macrosList[conference][macros])
				del(self.accessList[conference][macros])
		else:
			if(macros in  self.gMacrosList):
				del(self.gMacrosList[macros])
				del(self.gAccessList[macros])

	def expand(self, message, context, conference=None):
		macros = None
		rawBody = message.split(None, 1)
		command = rawBody[0].lower()
		param = (len(rawBody) == 2) and rawBody[1] or ''
		if(conference in self.macrosList):
			if(command in self.macrosList[conference]):
				macros = self.macrosList[conference][command]
		if(command in self.gMacrosList):
			macros = self.gMacrosList[command]
		if(not macros):
			return(message)
		message = self.replace(macros, param, context)
		expanded = self.expand(message, context, conference)
		return(expanded)

	def replace(self, message, param, context):
		if(message.count('$*')):
			message = message.replace('$*', param)
		else:
			param = param.split()
			paramLen = len(param)
			for i, n in enumerate(re.findall('\$[0-9]+', message)):
				if(i < paramLen):
					message = message.replace(n, param[i])
				else:
					message = message.replace(n, '')
		for i in self.parseCommand(message):
			cmd = [x.strip() for x in i.split(',')]
			res = self.proccess(cmd, context)
			if(res):
				message = message.replace('%%(%s)' % i, res)
		while(message.count('  ')):
			message = message.replace('  ', ' ')
		return(message)

	def getRand(self, args, source):
		try:
			f = int(args[0])
			t = int(args[1])
			return(str(random.randrange(f, t)))
		except:
			return('')

	def getContext(self, args, context):
		arg = args[0]
		if(arg == 'conf'):
			return(context[0])
		elif(arg == 'nick'):
			return(context[1])
		else:
			return('')

	def charMap(self, x, i):
		st = i['state']
		if(i['esc']):
			i['esc'] = False
			ret = i['level']
		elif(x == '\\'):
			i['esc'] = True
			ret = 0
		elif(x == '%'):
			i['state'] = 'cmd_p'
			ret = 0
		elif(x == '('):
			if(i['state'] == 'cmd_p'):
				i['level'] += 1
				i['state'] = 'args'
			ret=0
		elif(x == ')'):
			if(i['state'] == 'args'):
				i['state'] = 'null'
			ret = 0
		else:
			if(i['state'] == 'args'):
				ret = i['level']
			else:
				i['state'] = 'null'
				ret = 0
		return(ret)

	def getMap(self, inp):
		i = {'level': 0, 'state': 'null', 'esc': False}
		return([self.charMap(x, i) for x in list(inp)])

	def parseCommand(self, me):
		i = 0
		m = self.getMap(me)
		args = [''] * max(m)
		while(i < len(m)):
			if(m[i]):
				args[m[i]-1] += me[i]
			i += 1
		return(args)
		
	def execCommand(self, cmd, args, source):
		if(cmd in self.commands):
			return(self.commands[cmd](args, source))
		return('')

	def proccess(self, cmd, source):
		command = cmd[0]
		args = cmd[1:]
		return(self.execCommand(command, args, source))
