# coding: utf-8

# svn.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

URL_STRINGS = ("http://", "https://", "svn://")

def showSVNLog(msgType, conference, nick, param):
	if param:
		for x in URL_STRINGS:
			if param.startswith(x):
				param = param.split()
				if len(param) == 2:
					if count.isdigit():
						count = int(param[1])
					else:
						sendMsg(msgType, conference, nick, u"Читай помощь по команде")
						return
				else:
					count = 10
				url = param[0]
				pipe = os.popen("svn log %s --limit %d" % (url, count))
				message = pipe.read()
				pipe.close()
				enc = chardet.detect(message)["encoding"]
				sendMsg(msgType, conference, nick, unicode(message, enc))
				return

registerCommand(showSVNLog, u"svn", 10, 
				u"Показывает лог с svn", 
				u"svn <адрес> [кол-во]", 
				(u"svn http://jimm-fork.googlecode.com/svn/trunk 5", ), 
				ANY)
