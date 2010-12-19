# coding: utf-8

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

def pythonEval(msgType, conference, nick, param):
	try:
		sendMsg(msgType, conference, nick, unicode(eval(param)))
	except Exception:
		sendMsg(msgType, conference, nick, traceback.format_exc())

def pythonExec(msgType, conference, nick, param):
	try:
		exec(unicode(param) + "\n") in globals()
		sendMsg(msgType, conference, nick, u"Выполнено!")
	except Exception:
		sendMsg(msgType, conference, nick, traceback.format_exc())

def pythonShell(msgType, conference, nick, param):
	if "posix" == os.name:
		pipe = os.popen("sh -c \"%s\" 2>&1" % (param.encode("utf-8")))
	elif "nt" == os.name:
		pipe = os.popen(param.encode("utf-8"))
	message = pipe.read()
	pipe.close()
	if message:
		enc = chardet.detect(message)["encoding"]
		sendMsg(msgType, conference, nick, unicode(message, enc))
	else:
		sendMsg(msgType, conference, nick, u"Выполнено!")

def pythonCalc(msgType, conference, nick, param):
	if not re.sub("([0-9]+|[\+\-\/\*\^\.\(\)\|\&\^~])", "", param).strip():
		if not param.count("**"):
			try:
				sendMsg(msgType, conference, nick, str(eval(param)))
			except (ZeroDivisionError, SyntaxError):
				sendMsg(msgType, conference, nick, u"Научи меня это делать :)")
			except (MemoryError, OverflowError):
				sendMsg(msgType, conference, nick, u"Я не такая умная, чтоб сосчитать такое :(")
		else:
			sendMsg(msgType, conference, nick, u"Не буду такое считать")
	else:
		sendMsg(msgType, conference, nick, u"Ты глюк")

registerCommand(pythonEval, u"eval", 100, 
				u"Расчитывает и показывает заданное выражение питона", 
				u"<выражение>", 
				(u"str(gConferences)", ), 
				CMD_ANY | CMD_FROZEN | CMD_PARAM)
registerCommand(pythonExec, u"exec", 100, 
				u"Выполняет выражение питона", 
				u"<выражение>", 
				(u"del gConferences", ), 
				CMD_ANY | CMD_FROZEN | CMD_PARAM)
registerCommand(pythonShell, u"sh", 100, 
				u"Выполняет шелл-команду", 
				u"<команда>", 
				(u"ls", ), 
				CMD_ANY | CMD_FROZEN | CMD_PARAM)
registerCommand(pythonCalc, u"кальк", 10, 
				u"Калькулятор", 
				u"<выражение>", 
				(u"1 + 2", ), 
				CMD_ANY | CMD_PARAM)
