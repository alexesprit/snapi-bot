# coding: utf-8

# topic.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setTopic(msgType, conference, nick, param):
	message = protocol.Message(to=conference, typ=protocol.TYPE_PUBLIC)
	subject = param or ""
	message.setSubject(subject)
	gClient.send(message)
	if subject:
		sendMsg(msgType, conference, nick, u"Установила")
	else:
		sendMsg(msgType, conference, nick, u"Убрала")

registerCommand(setTopic, u"топег", 20, 
				u"Устанавливает тему в конференции", 
				u"<текст>", 
				(u"Ололо!", ), 
				CMD_CONFERENCE)
