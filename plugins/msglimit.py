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

def setMsgLimit(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param)
			if(param > 0):
				param = max(100, param)
				setConfigKey(conference, "msg", param)
				sendMsg(msgType, conference, nick, u"установлен лимит на %d символов" % (param))
			else:
				setConfigKey(conference, "msg", 0)
				sendMsg(msgType, conference, nick, u"ограничение на кол-во симолов отключено")
			saveChatConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"прочитай помощь по команде")
	else:
		limitValue = getConfigKey(conference, "msg")
		sendMsg(msgType, conference, nick, u"текущее значение: %d" % (limitValue))
		
def setMsgLimitState(conference):
	if(getConfigKey(conference, "msg") is None):
		setConfigKey(conference, "msg", 1500)

registerEvent(setMsgLimitState, ADDCONF)

registerCommand(setMsgLimit, u"мсглимит", 30, 
				u"Устанавливает или отключает (если указать 0) лимит на длину сообщения бота (большие сообщения будут перенаправляться в приват). Без параметра покажет текущее значение", 
				u"мсглимит [число]", 
				(u"мсглимит 0", u"мсглимит 1000"), 
				CHAT)
