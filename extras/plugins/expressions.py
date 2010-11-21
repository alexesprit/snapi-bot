# coding: utf-8;

# expressions.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

EXPRESSIONS_FILE = "expressions.txt"

gExpressions = {}

def saveExpressions(conference):
	path = getConfigPath(conference, EXPRESSIONS_FILE);
	utils.writeFile(path, str(gExpressions[conference]));

def freeExpressions(conference):
	del gExpressions[conference]

def loadExpressions(conference):
	path = getConfigPath(conference, EXPRESSIONS_FILE)
	utils.createFile(path, "{}")
	gExpressions[conference] = eval(utils.readFile(path))

def addExpression(msgType, conference, nick, param):
	param = param.split("=", 1)
	if len(param) == 2:
		exp = param[0].strip()
		text = param[1].strip()
		if exp and text:
			if exp in gExpressions:
				gExpressions[conference][exp] = text
				sendMsg(msgType, conference, nick, u"заменила")
			else:
				gExpressions[conference][exp] = text
				sendMsg(msgType, conference, nick, u"добавила")
			saveExpressions(conference);
		else:
			sendMsg(msgType, conference, nick, u"ошибочный запрос")
	else:
		sendMsg(msgType, conference, nick, u"читай справку по команде")

def delExpression(msgType, conference, nick, param):
	if param in gExpressions[conference]:
		del gExpressions[conference][param]
		saveExpressions(conference)
		sendMsg(msgType, conference, nick, u"удалила")
	else:
		sendMsg(msgType, conference, nick, u"такого выражения нет")

def showExpressions(msgType, conference, nick, param):
	if gExpressions[conference]:
		items = [exp for exp in gExpressions[conference]]
		message = u"выражения:\n%s" % ("\n".join(items))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"выражений нет");		

def showExprInfo(msgType, conference, nick, param):
	if param in gExpressions[conference]:
		sendMsg(msgType, conference, nick, gExpressions[conference][param])
	else:
		sendMsg(msgType, conference, nick, u"такого выражения нет")	

def processExpression(stanza, msgType, conference, nick, trueJid, text):
	if nick != getBotNick(conference):
		text = text.lower()
		command = text.split()[0]
		if not isCommand(command):
			for exp in gExpressions[conference]:
				try:
					if re.search(exp, text, re.DOTALL):
						sendMsg(msgType, conference, nick, gExpressions[conference][exp])
						return
				except re.error:
					pass

registerEvent(loadExpressions, EVT_ADDCONFERENCE)
registerEvent(freeExpressions, EVT_DELCONFERENCE)

registerMessageHandler(processExpression, H_CONFERENCE)

registerCommand(addExpression, u"выражение+", 20, 
				u"Добавить регулярное выражение", 
				u"<выражение=текст>", 
				(u"где(.+)\?=гугли", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delExpression, u"выражение-", 20, 
				u"Удалить регулярное выражение", 
				u"<выражение>", 
				(u"где(.+)\?", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showExpressions, u"выражения", 20, 
				u"Показывает все регулярные выражения. Синтаксис аналогичен регулярным выражениям языка Python", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(showExprInfo, u"выражение*", 20, u"Показывает информацию о регулярном выражении", 
				u"<выражение>", 
				(u"где(.*?)?", ), 
				CMD_CONFERENCE | CMD_PARAM)