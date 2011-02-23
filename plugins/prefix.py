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

def setDefaultPrefixValue(conference):
	if getConferenceConfigKey(conference, "prefix") is None:
		setConferenceConfigKey(conference, "prefix", "")

def managePrefixControl(msgType, conference, nick, param):
	if param:
		args = param.split()
		if len(args) == 1:
			prefix = args[0]
			if prefix.lower() != "none":
				setConferenceConfigKey(conference, "prefix", prefix)
				sendMsg(msgType, conference, nick, u"Установлен префикс: %s" % (prefix))
			else:
				setConferenceConfigKey(conference, "prefix", "")
				sendMsg(msgType, conference, nick, u"Префикс для команд отключен")
			saveConferenceConfig(conference)
	else:
		prefixValue = getConferenceConfigKey(conference, "prefix")
		if prefixValue:
			sendMsg(msgType, conference, nick, u"Текущее значение: %s" % (prefixValue))
		else:
			sendMsg(msgType, conference, nick, u"Префикс не установлен")

registerEventHandler(setDefaultPrefixValue, EVT_ADDCONFERENCE)
registerCommand(managePrefixControl, u"префикс", 30, 
				u"Устанавливает или отключает (если указать None) префикс для команд. Без параметра покажет текущее значение", 
				u"[что-то]", 
				(None, u"None", u"_"), 
				CMD_CONFERENCE)
