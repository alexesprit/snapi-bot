# coding: utf-8

# notices.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def noticeControl(msgType, conference, nick, param):
	if param:
		if param.isdigit():
			param = int(param)
			if param == 1:
				setConferenceConfigKey(conference, "notices", 1)
				sendMsg(msgType, conference, nick, u"Оповещения включены")
			else:
				setConferenceConfigKey(conference, "notices", 0)
				sendMsg(msgType, conference, nick, u"Оповещения выключены")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"Текущее значение: %s" % (getConferenceConfigKey(conference, "popups")))

def sendNotices(msgType, conference, nick, param):
	conferences = getConferences()
	count = 0
	for conf in conferences:
		if getConferenceConfigKey(conf, "notices"):
			sendToConference(conf, u"Новости от администрации:\n%s" % param)
			count += 1
	sendMsg(msgType, conference, nick, "Сообщение ушло в %d конференций из %d" % (count, len(conferences)))

def setDefNoticeValue(conference):
	if getConferenceConfigKey(conference, "notices") is None:
		setConferenceConfigKey(conference, "notices", 1)

registerEvent(setDefNoticeValue, ADDCONF)

registerCommand(noticeControl, u"оповещения", 30, 
				u"Отключает (0) или включает (1) сообщения о новостях. Без параметра покажет текущее значение", 
				u"[0|1]", 
				(None, u"0"), 
				CHAT)
registerCommand(sendNotices, u"оповещение", 100, 
				u"Отправляет сообщение по всем конференциям, в которых сидит бот", 
				u"<сообщение>", 
				(u"привет!11", ), 
				ANY | PARAM)
