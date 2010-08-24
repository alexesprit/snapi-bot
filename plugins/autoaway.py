# coding: utf-8;

# autoaway.py
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

CFG_AUTOAWAY = 'autoaway';

def autoAwayControl(type, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param);
			if(param == 1):
				setConfigKey(conference, CFG_AUTOAWAY, 1);
				sendMsg(type, conference, nick, u'автоотсутствие включено');
				if(not hasAwayTimer(conference)):
					createAwayTimer(conference);
			else:
				setConfigKey(conference, CFG_AUTOAWAY, 0);
				sendMsg(type, conference, nick, u'автоотсутствие отключено');
				if(hasAwayTimer(conference)):
					stopAwayTimer(conference);
			saveChatConfig(conference);
		else:
			sendMsg(type, conference, nick, u'прочитай помощь по команде');
	else:
		sendMsg(type, conference, nick, u'текущее значение: %d' % (getConfigKey(conference, CFG_AUTOAWAY)));

registerCommandHandler(autoAwayControl, u'автостатус', 30, u'Отключает (0) или включает (1) автосмену статуса бота на away при отсутствии команд в течении %s Без параметра покажет текущее значение' % (time2str(IDLE_TIMEOUT)), u'автостатус [0/1]', (u'автостатус', u'автостатус 0'), CHAT);

def setAutoawayState(conference):
	if(getConfigKey(conference, CFG_AUTOAWAY) is None):
		setConfigKey(conference, CFG_AUTOAWAY, 1);

registerPluginHandler(setAutoawayState, ADD_CHAT);
