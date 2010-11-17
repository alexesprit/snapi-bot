# coding: utf-8

# msglimit.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setDefMsgLimitValue(conference):
	if getConferenceConfigKey(conference, "msg") is None:
		setConferenceConfigKey(conference, "msg", 1500)

def manageMsgLimitValue(msgType, conference, nick, param):
	if param:
		if param.isdigit():
			param = int(param)
			if param > 0:
				param = max(100, param)
				setConferenceConfigKey(conference, "msg", param)
				sendMsg(msgType, conference, nick, u"Установлен лимит на %d символов" % (param))
			else:
				setConferenceConfigKey(conference, "msg", 0)
				sendMsg(msgType, conference, nick, u"Ограничение на кол-во симолов отключено")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		limitValue = getConferenceConfigKey(conference, "msg")
		sendMsg(msgType, conference, nick, u"Текущее значение: %d" % (limitValue))

registerEvent(setDefMsgLimitValue, ADDCONF)
registerCommand(manageMsgLimitValue, u"мсглимит", 30, 
				u"Устанавливает или отключает (если указать 0) лимит на длину сообщения бота (большие сообщения будут перенаправляться в приват). Без параметра покажет текущее значение", 
				u"[число]", 
				(u"0", u"1000"), 
				CHAT)
