# coding: utf-8;

# truejid.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showTrueJid(type, conference, nick, param):
	if(nickInConference(conference, param)):
		if(PUBLIC == type):
			sendMsg(type, conference, nick, u'смотри в привате');
		trueJid = getTrueJid(conference, param);
		sendMsg(PRIVATE, conference, nick, u'реальный жид %s: %s' % (param, trueJid));

registerCommand(showTrueJid, u'тружид', 20, u'Показывает реальный жид указанного ника', u'тружид <ник>', (u'тружид guy', ), CHAT | PARAM);
