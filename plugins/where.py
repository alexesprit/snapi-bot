# coding: utf-8;

# where.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showWhereIsBot(type, conference, nick, param):
	confCount = len(getConferences());
	if(confCount):
		message = u'я сижу в %d конфах:\n' % (confCount);
		infoList = [u'%s (%d чел.)' % (conf, len(getJidList(conf))) for conf in getConferences()];
		message += '\n'.join(infoList);
		sendMsg(type, conference, nick, message);
	else:
		sendMsg(type, conference, nick, u'я пока нигде не сижу');

registerCommand(showWhereIsBot, u'хдебот', 10, u'Показывает, в каких конфах сидит бот', None, (u'хдебот', ), ANY | NONPARAM);
