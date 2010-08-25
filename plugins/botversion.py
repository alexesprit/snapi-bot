# coding: utf-8;

# botversion.py
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

VER_FILE = 'config/version.txt';

def setBotVersion(type, conference, nick, param):
	global gVersion;
	if(not param):
		sendMsg(type, conference, nick, u'|'.join(gVersion));
	elif(param.count('|') == 2):
		gVersion = tuple(param.split('|'));
		writeFile(VER_FILENAME, str(gVersion));
		sendMsg(type, conference, nick, u'поняла, сейчас поставлю');

registerCommand(setBotVersion, u'ботверсия', 100, u'Выставляет версию клиента у бота. Без параметра покажет текущее значение', u'ботверсия [клиент|версия|ось]', (u'ботверсия', u'ботверсия Jimm|0.6.4|Nokia 3310'), ROSTER);

def loadBotVersion():
	global gVersion;
	createFile(VER_FILE, str(gVersion));
	gVersion = eval(readFile(VER_FILE));

registerEvent(loadBotVersion, STARTUP);
