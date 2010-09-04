# coding: utf-8;

# popup.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CFG_POPUPS = 'popups';

def isPopupEnabled(conference):
	return(getConfigKey(conference, CFG_POPUPS));

def popupsControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param);
			if(param == 1):
				setConfigKey(conference, CFG_POPUPS, 1);
				sendMsg(msgType, conference, nick, u'оповещения включены');
			else:
				setConfigKey(conference, CFG_POPUPS, 0);
				sendMsg(msgType, conference, nick, u'оповещения выключены');
			saveChatConfig(conference);
		else:
			sendMsg(msgType, conference, nick, u'прочитай помощь по команде');
	else:
		sendMsg(msgType, conference, nick, u'текущее значение: %s' % (getConfigKey(conference, CFG_POPUPS)));
	
def setPopupsState(conference):
	if(getConfigKey(conference, CFG_POPUPS) is None):
		setConfigKey(conference, CFG_POPUPS, 1);

registerEvent(setPopupsState, ADDCONF);
registerCommand(popupsControl, u'оповещения', 30, u'Отключает (0) или включает (1) сообщения о рестартах/выключениях, а также глобальные новости. Без параметра покажет текущее значение', u'оповещения [0/1]', (u'оповещения', u'оповещения 0'), CHAT);
