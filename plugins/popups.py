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

def popupControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param);
			if(param == 1):
				setConfigKey(conference, 'popups', 1);
				sendMsg(msgType, conference, nick, u'оповещения включены');
			else:
				setConfigKey(conference, 'popups', 0);
				sendMsg(msgType, conference, nick, u'оповещения выключены');
			saveChatConfig(conference);
		else:
			sendMsg(msgType, conference, nick, u'прочитай помощь по команде');
	else:
		sendMsg(msgType, conference, nick, u'текущее значение: %s' % (getConfigKey(conference, 'popups')));
	
def setPopupState(conference):
	if(getConfigKey(conference, 'popups') is None):
		setConfigKey(conference, 'popups', 1);

registerEvent(setPopupState, ADDCONF);
registerCommand(popupControl, u'оповещения', 30, \
				u'Отключает (0) или включает (1) сообщения о рестартах/выключениях, а также глобальные новости. Без параметра покажет текущее значение', \
				u'оповещения [0|1]', (u'оповещения', u'оповещения 0'), CHAT);
