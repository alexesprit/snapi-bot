# coding: utf-8

# prefix.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setDefPrefixValue(conference):
	if(getConfigKey(conference, "prefix") is None):
		setConfigKey(conference, "prefix", "")

def managePrefixControl(msgType, conference, nick, param):
	if(param):
		if(param.lower() != "none"):
			setConfigKey(conference, "prefix", param)
			sendMsg(msgType, conference, nick, u"установлен префикс: %s" % (param))
		else:
			setConfigKey(conference, "prefix", "")
			sendMsg(msgType, conference, nick, u"префикс для команд отключен")
		saveConferenceConfig(conference)
	else:
		prefixValue = getConfigKey(conference, "prefix")
		if(prefixValue):
			sendMsg(msgType, conference, nick, u"текущее значение: %s" % (prefixValue))
		else:
			sendMsg(msgType, conference, nick, u"префикс не установлен")

registerEvent(setDefPrefixValue, ADDCONF)
registerCommand(managePrefixControl, u"префикс", 30, 
				u"Устанавливает или отключает (если указать None) префикс для команд. Без параметра покажет текущее значение", 
				u"префикс [что-то]", 
				(u"префикс _", u"префикс None"), 
				CHAT)
