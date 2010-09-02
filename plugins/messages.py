# coding: utf-8;

# messages.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def sendToAdmins(msgType, conference, nick, param):
	for admin in gAdmins:
		msg(admin, u'Сообщение от %s из %s:\n%s' % (conference, nick, param));
	sendMsg(msgType, conference, nick, u'ваше сообщение отправлено');

def sendToConferences(msgType, conference, nick, param):
	conferences = getConferences();
	count = 0;
	for conf in conferences:
		if(isPopupEnabled(conf)):
			sendToConference(conf, u'Новости от администрации:\n%s' % param);
			count += 1;
	sendMsg(msgType, conference, nick, 'мессага ушла в %d конференций из %d' % (count, len(conferences)));
	
def messageToChat(msgType, conference, nick, param):
	sendToConference(conference, param);

registerCommand(sendToConferences, u'мессага_конфам', 100, u'Отправляет сообщение по всем конференциям, в которых сидит бот', u'мессага_конфам [сообщение]', (u'мессага_конфам привет!11'), ANY | PARAM);
registerCommand(sendToAdmins, u'мессага_админу', 10, u'Отправляет сообщение всем администраторам бота', u'мессага_админу <сообщение>', (u'мессага_админу привет!11'), ANY | PARAM);
registerCommand(messageToChat, u'сказать', 20, u'Говорить через бота в конференции', u'сказать <сообщение>', (u'сказать салют пиплы', ), CHAT | PARAM);
