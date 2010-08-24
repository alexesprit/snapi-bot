# coding: utf-8;

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

import os, random, re;
import __main__, xmpp;

def getRand(args, source):
	try:
		f = int(args[0]);
		t = int(args[1]);
		return(str(random.randrange(f, t)));
	except:
		return('');

def getContext(args, context):
	arg = args[0];
	if(arg == 'conf'):
		return(context[0]);
	elif(arg == 'nick'):
		return(context[1]);
	else:
		return('');

class MacroCommands:
	commands = {
		'rand': getRand,
		'context': getContext
	};

	def charMap(self, x, i):
		st = i['state'];
		if(i['esc']):
			i['esc'] = False;
			ret = i['level'];
		elif(x == '\\'):
			i['esc'] = True;
			ret = 0;
		elif(x == '%'):
			i['state'] = 'cmd_p';
			ret = 0;
		elif(x == '('):
			if(i['state'] == 'cmd_p'):
				i['level'] += 1;
				i['state'] = 'args';
			ret=0
		elif(x == ')'):
			if(i['state'] == 'args'):
				i['state'] = 'null';
			ret = 0;
		else:
			if(i['state'] == 'args'):
				ret = i['level'];
			else:
				i['state'] = 'null';
				ret = 0;
		return(ret);

	def getMap(self, inp):
		i = {'level': 0, 'state': 'null', 'esc': False};
		return([self.charMap(x, i) for x in list(inp)]);

	def parseCommand(self, me):
		i = 0;
		m = self.getMap(me);
		args = [''] * max(m);
		while(i < len(m)):
			if(m[i]):
				args[m[i]-1] += me[i];
			i += 1;
		return(args);
		
	def execCommand(self, cmd, args, source):
		if(cmd in self.commands):
			return(self.commands[cmd](args, source));
		return('');

	def proccess(self, cmd, source):
		command = cmd[0];
		args = cmd[1:];
		return(self.execCommand(command, args, source));

class Macros:
	gMacrosList = {};
	gAccessList = {};

	macrosList = {};
	accessList = {};
	macroCommands = MacroCommands();

	def loadMacroses(self, groupChat = None):
		if(groupChat):
			macrosFileName = 'config/%s/macros.txt' % (groupChat);
			accessFileName = 'config/%s/macrosaccess.txt' % (groupChat);
			
			__main__.createFile(macrosFileName, '{}');
			__main__.createFile(accessFileName, '{}');

			self.macrosList[groupChat] = eval(__main__.readFile(macrosFileName));
			self.accessList[groupChat] = eval(__main__.readFile(accessFileName));
		else:
			macrosFileName = 'config/macros.txt';
			accessFileName = 'config/macrosaccess.txt';
			
			__main__.createFile(macrosFileName, '{}');
			__main__.createFile(accessFileName, '{}');

			self.gMacrosList = eval(__main__.readFile(macrosFileName));
			self.gAccessList = eval(__main__.readFile(accessFileName));

	def saveMacroses(self, groupChat = None):
		if(groupChat):
			for x in self.macrosList.keys():
				__main__.writeFile('config/' + x + '/macros.txt', str(self.macrosList[x]));
			for x in self.accessList.keys():
				__main__.writeFile('config/' + x + '/macrosaccess.txt', str(self.accessList[x]));
		else:
			__main__.writeFile('config/macros.txt', str(self.gMacrosList));
			__main__.writeFile('config/macrosaccess.txt', str(self.gAccessList));
			
	def unloadMacroses(self, groupChat):
		if(groupChat in self.macrosList):
			del(self.macrosList[groupChat]);

	def getMacrosList(self, groupChat = None):
		if(groupChat):
			return(self.macrosList[groupChat].keys());
		else:
			return(self.gMacrosList.keys());

	def getMacros(self, macros, groupChat = None):
		if(groupChat):
			return(self.macrosList[groupChat].get(macros));
		else:
			return(self.gMacrosList.get(macros));
		
	def hasMacros(self, macros, groupChat = None):
		if(groupChat):
			return(macros in self.macrosList[groupChat]);
		else:
			return(macros in self.gMacrosList);
			
	def getAccess(self, macros, groupChat = None):
		if(groupChat):
			return(self.accessList[groupChat].get(macros));
		else:
			return(self.gAccessList[macros]);

	def setAccess(self, macros, access, groupChat = None):
		if(groupChat):
			self.accessList[groupChat][macros] = access;
		else:
			self.gAccessList[macros] = access;

	def add(self, macros, param, access, groupChat = None):
		if(groupChat):
			self.macrosList[groupChat][macros] = param;
		else:
			self.gMacrosList[macros] = param;
		self.setAccess(macros, access, groupChat);

	def remove(self, macros, groupChat = None):
		if(groupChat):
			if(macros in self.macrosList[groupChat]):
				del(self.macrosList[groupChat][macros]);
				del(self.accessList[groupChat][macros]);
		else:
			if(macros in  self.gMacrosList):
				del(self.gMacrosList[macros]);
				del(self.gAccessList[macros]);

	def expand(self, cmd, context, conference = None):
		exp = None;
		cl = self.parseCommand(cmd);
		command = cl[0].split()[0].lower();
		param = cl[1:];
		if(conference in self.macrosList):
			if(command in self.macrosList[conference]):
				exp = self.replace(self.macrosList[conference][command], param, context);
		if(command in self.gMacrosList):
			exp = self.replace(self.gMacrosList[command], param, context);
		if(not exp):
			return(cmd);
		rexp = self.expand(exp, context, conference);
		return(rexp);

	def replace(self, macros, param, context):
		expanded = macros;
		if(expanded.count('$*')):
			expanded = expanded.replace('$*', ' '.join(param));
		else:
			for i, n in enumerate(re.findall('\$[0-9]+', expanded)):
				if(len(param) <= i):
					break;
				expanded = expanded.replace(n, param[i]);
		for i in self.macroCommands.parseCommand(expanded):
			cmd = [x.strip() for x in i.split(',')];
			res = self.macroCommands.proccess(cmd, context);
			if(res):
				expanded = expanded.replace('%%(%s)' % i, res);
		return(expanded);

	def charMap(self, x, i):
		ret = i['level'];
		if(i['esc']):
			i['esc'] = False;
		elif(x == '('):
			i['context'] = True;
		elif(x == ')'):
			i['context'] = False;
		elif(x == '\\'):
			i['esc'] = True;
			ret = 0;
		elif(x == '`'):
			i['arg'] = not i['arg'];
			ret = 0;
		elif(x == ' '):
			if(not i['arg'] and not i['context']):
				i['level'] += 1;
				ret = 0;
		return(ret);

	def getMap(self, inp):
		i = {'arg': False, 'context': False, 'level': 1, 'esc': False};
		return([self.charMap(x, i) for x in list(inp)]);

	def parseCommand(self, cmd):
		i = 0;
		m = self.getMap(cmd);
		args = [''] * max(m);
		while(i < len(m)):
			if(m[i]):
				args[m[i]-1] += cmd[i];
			i += 1;
		return(args);
