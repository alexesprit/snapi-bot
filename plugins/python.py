# coding: utf-8;

# python.py
# Initial Copyright (с) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (с) 2007 Als <Als@exploit.in>
# Parts of code Copyright (с) Bohdan Turkynewych aka Gh0st <tb0hdan[at]gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def pythonEval(type, conference, nick, param):
	try:
		sendMsg(type, conference, nick, unicode(eval(param)));
	except(Exception):
		sendMsg(type, conference, nick, traceback.format_exc());

def pythonExec(type, conference, nick, param):
	try:
		exec(unicode(param)) in globals();
	except(Exception):
		sendMsg(type, conference, nick, traceback.format_exc());

def pythonShell(type, conference, nick, param):
	if(os.name == 'posix'):
		pipe = os.popen('sh -c "%s" 2>&1' % (param.encode('utf8')));
		sendMsg(type, conference, nick, pipe.read());
	elif(os.name == 'nt'):
		pipe = os.popen('%s' % (param.encode('utf8')));
		sendMsg(type, conference, nick, pipe.read().decode('cp866'));
	pipe.close;

def pythonCalc(type, conference, nick, param):
	if(re.sub('([0-9]+|[\+\-\/\*\^\.()])', '', param).strip() == ''):
		if(not param.count('**')):
			try:
				sendMsg(type, conference, nick, str(eval(param)));
			except(ZeroDivisionError):
				sendMsg(type, conference, nick, u'научи меня это делать :)');		
		else:
			sendMsg(type, conference, nick, u'не буду такое считать');
	else:
		sendMsg(type, conference, nick, u'ты глюк');

registerCommandHandler(pythonEval, u'eval', 100, u'Расчитывает и показывает заданное выражение питона', u'eval <выражение>', (u'eval str(1)'), ANY | FROZEN | PARAM);
registerCommandHandler(pythonExec, u'exec', 100, u'Выполняет выражение питона', u'exec <выражение>', (u'exec del(GROUPCHATS)', ), ANY | FROZEN | PARAM);
registerCommandHandler(pythonShell, u'sh', 100, u'Выполняет шелл-команду', u'sh <команда>', (u'sh ls'), ANY | FROZEN | PARAM);
registerCommandHandler(pythonCalc, u'кальк', 10, u'Калькулятор', u'калк <выражение>', (u'калк 1 + 2'), ANY | PARAM);
