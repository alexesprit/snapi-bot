# coding: utf-8;

# manage.py
# Initial Copyright (c) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def joinToConference(type, conference, nick, param):
	param = param.split();
	if(param and param[0].count('@')):
		conf = param[0];
		if(chatInList(conf)):
			sendMsg(type, conference, nick, u'я уже там!');
		else:
			password = (len(param) == 2) and param[1] or None;
			addConference(conf);
			time.sleep(1);
			joinConference(conf, gBotNick, getConfigKey(conf, 'password'));
			saveChatConfig(conf);
			sendMsg(type, conference, nick, u'зашла');

def leaveAConference(type, conference, nick, param):
	conf = param or conference;
	if(chatInList(conf)):
		if(not chatInList(conference)):
			sendMsg(type, conference, nick, u'ушла');
		leaveConference(conf, u'меня уводит %s' % (nick));
	else:
		sendMsg(type, conference, nick, u'а меня там нету');

registerCommandHandler(joinToConference, u'зайти', 100, u'Зайти в определённую конференцию', u'зайти <конференция> [пароль]', (u'зайти test@conference.jabber.aq', u'зайти test@conference.jabber.ru 1234'));
registerCommandHandler(leaveAConference, u'свали', 30, u'Заставляет выйти из текущей или определённой конференции', u'свали [конференция]', (u'свали test@conference.jabber.ru', u'свали'));
