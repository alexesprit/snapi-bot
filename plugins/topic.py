# coding: utf-8;

# topic.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setTopic(msgType, conference, nick, param):
	message = xmpp.Message(to = conference, typ = PUBLIC, subject = param);
	gClient.send(message);
	sendMsg(msgType, conference, nick, u'поставила');

registerCommand(setTopic, u'топег', 20, u'Устанавливает тему в конференции', u'топег <текст>', (u'топег ололо', ), CHAT | PARAM);
