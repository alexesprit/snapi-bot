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


AUTH_QUESTIONS = (
	(u"сорок + три", "43"),
	(u"60 + четыре", "64"),
	(u"десять + 22", "32"),
	(u"17 + девять", "26"),
	(u"12 + восемь", "20"),
	(u"сто - шесть", "94"),
	(u"сорок * два", "80")
)

gAuthAnswer = {}

def setDefAuthValue(conference):
	if(getConfigKey(conference, "auth") is None):
		setConfigKey(conference, "auth", 0)

def initAuthCache(conference):
	gAuthAnswer[conference] = {}

def freeAuthCache(conference):
	del(gAuthAnswer[conference])

def askAuthQuestion(conference, nick, trueJid, aff, role):
	if(getConfigKey(conference, "auth")):
		if(aff == protocol.AFF_NONE):
			question, answer = random.choice(AUTH_QUESTIONS)
			setMUCRole(conference, nick, protocol.ROLE_VISITOR, u"Неавторизованый участник")
			message = u"Чтобы получить голос, реши пример: %s. Как решишь, напиши мне ответ" % (question)
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
			gAuthAnswer[conference][trueJid] = answer

def clearAuthCache(conference, nick, trueJid, reason, code):
	if(trueJid in gAuthAnswer[conference]):
		del(gAuthAnswer[conference][trueJid])

def authAnswerListener(stanza, msgType, conference, nick, trueJid, body):
	if(protocol.TYPE_PRIVATE == msgType):
		if(trueJid in gAuthAnswer[conference]):
			if(gAuthAnswer[conference][trueJid] == body):
				sendMsg(msgType, conference, nick, u"Признаю - ты не бот :)")
				setMUCRole(conference, nick, protocol.ROLE_PARTICIPANT, u"Авторизация пройдена")
				del(gAuthAnswer[conference][trueJid])
			else:
				sendMsg(msgType, conference, nick, u"Неправильный ответ")

def manageAuthValue(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param)
			if(param == 1):
				setConfigKey(conference, "auth", 1)
				sendMsg(msgType, conference, nick, u"Авторизация включена")
			else:
				setConfigKey(conference, "auth", 0)
				sendMsg(msgType, conference, nick, u"Авторизация отключена")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"Прочитай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"Текущее значение: %d" % (getConfigKey(conference, "auth")))

registerEvent(setDefAuthValue, ADDCONF)
registerEvent(initAuthCache, ADDCONF)
registerEvent(freeAuthCache, DELCONF)

registerJoinHandler(askAuthQuestion)
registerLeaveHandler(clearAuthCache)

registerMessageHandler(authAnswerListener, CHAT)

registerCommand(manageAuthValue, u"авторизация", 30, 
				u"Отключает (0) или включает (1) проверку вошедшего пользователя на человечность. Без параметра покажет текущее значение", 
				u"авторизация [0|1]", 
				(u"авторизация", u"авторизация 0"), 
				CHAT)
