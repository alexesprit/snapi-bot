# coding: utf-8;

# jokes.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CFG_JOKES = 'jokes';

def jokesControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param);
			if(param == 1):
				setConfigKey(conference, CFG_JOKES, 1);
				sendMsg(msgType, conference, nick, u'шуточки включены');
			else:
				setConfigKey(conference, CFG_JOKES, 0);
				sendMsg(msgType, conference, nick, u'шуточки отключены');
			saveChatConfig(conference);
		else:
			sendMsg(msgType, conference, nick, u'прочитай помощь по команде');
	else:
		sendMsg(msgType, conference, nick, u'текущее значение: %d' % (getConfigKey(conference, CFG_JOKES)));

registerCommand(jokesControl, u'шуточки', 30, u'Отключает (0) или включает (1) шуточки, которыми бот порою подменяет ответ. Без параметра покажет текущее значение', u'шуточки [0/1]', (u'шуточки', u'шуточки 0'), CHAT);

def setJokesState(conference):
	if(getConfigKey(conference, CFG_JOKES) is None):
		setConfigKey(conference, CFG_JOKES, 1);

registerEvent(setJokesState, ADDCONF);

def loadJokes():
	global gJokes;
	gJokes = eval(readFile('resource/jokes.txt', 'utf-8'));

registerEvent(loadJokes, STARTUP);
