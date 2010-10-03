# coding: utf-8

# auth.py
# Initial Copyright (c) ???
# Modification Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

AA = {"question": u"сорок + семь", "answer": "47"}
AB = {"question": u"60 + четыре", "answer": "64"}
AC = {"question": u"тридцать + 2", "answer": "32"}
AD = {"question": u"7 + девять", "answer": "16"}
AE = {"question": u"2 + шесть", "answer": "8"}
AF = {"question": u"2 + два", "answer": "4"}
AG = {"question": u"один + один", "answer": "2"}

gAuthAnswer = {}

def setAuthState(conference):
	gAuthAnswer[conference] = {}
	if(getConfigKey(conference, "auth") is None):
		setConfigKey(conference, "auth", 0)

def unloadAuthCache(conference):
	del(gAuthAnswer[conference])

def askAuthQuestion(conference, nick, trueJid, aff, role):
	if(getConfigKey(conference, "auth")):
		if(aff == xmpp.AFF_NONE):
			question = random.choice((AA, AB, AC, AD, AE, AF, AG, ))
			setRole(conference, nick, xmpp.ROLE_VISITOR, u"неавторизованый участник")
			message = u"Чтобы получить голос, реши пример: %(question)s. Как решишь, напиши мне ответ" % (question)
			sendMsg(xmpp.TYPE_PRIVATE, conference, nick, message)
			gAuthAnswer[conference][trueJid] = question["answer"]

def clearAuthCache(conference, nick, trueJid, reason, code):
	if(trueJid in gAuthAnswer[conference]):
		del(gAuthAnswer[conference][trueJid])

def authAnswerListener(stanza, msgType, conference, nick, trueJid, body):
	if(xmpp.TYPE_PRIVATE == msgType):
		if(trueJid in gAuthAnswer[conference]):
			if(gAuthAnswer[conference][trueJid] == body):
				sendMsg(msgType, conference, nick, u"ок, признаю - ты не бот =)")
				setRole(conference, nick, xmpp.ROLE_PARTICIPANT, u"авторизация пройдена")
				del(gAuthAnswer[conference][trueJid])
			else:
				sendMsg(msgType, conference, nick, u"неправильный ответ. подумай или заюзай гугл")

def authControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param)
			if(param == 1):
				setConfigKey(conference, "auth", 1)
				sendMsg(msgType, conference, nick, u"авторизация включена")
			else:
				setConfigKey(conference, "auth", 0)
				sendMsg(msgType, conference, nick, u"авторизация отключена")
			saveChatConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"прочитай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"текущее значение: %d" % (getConfigKey(conference, "auth")))

registerEvent(setAuthState, ADDCONF)
registerEvent(unloadAuthCache, DELCONF)

registerJoinHandler(askAuthQuestion)
registerLeaveHandler(clearAuthCache)

registerMessageHandler(authAnswerListener, CHAT)

registerCommand(authControl, u"авторизация", 30, 
				u"Отключает (0) или включает (1) проверку вошедшего пользователя на человечность. Без параметра покажет текущее значение", 
				u"авторизация [0|1]", 
				(u"авторизация", u"авторизация 0"), 
				CHAT)
