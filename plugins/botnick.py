# coding: utf-8;

# botnick.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setBotNick(msgType, conference, nick, param):
	joinConference(conference, param, getConfigKey(conference, 'password'));
	saveChatConfig(conference);
	sendMsg(msgType, conference, nick, u'запомнила');

registerCommand(setBotNick, u'ботник', 30, u'Меняет ник бота', u'ботник <ник>', (u'ботник ПеЛоТкО.о', ), CHAT | PARAM);
