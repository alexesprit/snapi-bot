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

def initAuthCache(conference):
	gAuthAnswer[conference] = {}

def freeAuthCache(conference):
	del gAuthAnswer[conference]

def setDefaultAuthValue(conference):
	if getConferenceConfigKey(conference, "auth") is None:
		setConferenceConfigKey(conference, "auth", 0)

def manageAuthValue(msgType, conference, nick, param):
	if param:
		if param.isdigit():
			param = int(param)
			if param == 1:
				setConferenceConfigKey(conference, "auth", 1)
				sendMsg(msgType, conference, nick, u"Авторизация включена")
			else:
				setConferenceConfigKey(conference, "auth", 0)
				sendMsg(msgType, conference, nick, u"Авторизация отключена")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"Прочитай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"Текущее значение: %d" % (getConferenceConfigKey(conference, "auth")))		

def askAuthQuestion(conference, nick, truejid, aff, role):
	if getConferenceConfigKey(conference, "auth"):
		if aff == protocol.AFF_NONE:
			question, answer = random.choice(AUTH_QUESTIONS)
			setMUCRole(conference, nick, protocol.ROLE_VISITOR, u"Неавторизованый участник")
			message = u"Чтобы получить голос, реши пример: %s. Как решишь, напиши мне ответ" % (question)
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
			gAuthAnswer[conference][truejid] = answer

def authAnswerListener(stanza, msgType, conference, nick, truejid, body):
	if protocol.TYPE_PRIVATE == msgType:
		if truejid in gAuthAnswer[conference]:
			if gAuthAnswer[conference][truejid] == body:
				sendMsg(msgType, conference, nick, u"Признаю - ты не бот :)")
				setMUCRole(conference, nick, protocol.ROLE_PARTICIPANT, u"Авторизация пройдена")
				del gAuthAnswer[conference][truejid]
			else:
				sendMsg(msgType, conference, nick, u"Неправильный ответ")

def clearAuthCache(conference, nick, truejid, reason, code):
	if truejid in gAuthAnswer[conference]:
		del gAuthAnswer[conference][truejid]

registerEventHandler(initAuthCache, EVT_ADDCONFERENCE)
registerEventHandler(freeAuthCache, EVT_DELCONFERENCE)

registerEventHandler(setDefaultAuthValue, EVT_ADDCONFERENCE)

registerEventHandler(askAuthQuestion, EVT_USERJOIN)
registerEventHandler(authAnswerListener, EVT_MSG | H_CONFERENCE)

registerEventHandler(clearAuthCache, EVT_USERLEAVE)

registerCommand(manageAuthValue, u"авторизация", 30, 
				u"Отключает (0) или включает (1) проверку вошедшего пользователя на человечность. Без параметра покажет текущее значение", 
				u"[0|1]", 
				(None, u"0"), 
				CMD_CONFERENCE)
