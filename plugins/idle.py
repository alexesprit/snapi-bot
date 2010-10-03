# coding: utf-8

# idle.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showUserIdleTime(msgType, conference, nick, param):
	if(nickIsOnline(conference, param)):
		idleTime = int(time.time() - getNickKey(conference, param, NICK_IDLE))
		sendMsg(msgType, conference, nick, u"%s заснул %s назад" % (param, time2str(idleTime)))
	else:
		sendMsg(msgType, conference, nick, u"а это кто?")

registerCommand(showUserIdleTime, u"жив", 10, 
				u"Показывает время неактивности пользователя", 
				u"жив <ник>", 
				(u"жив Nick", ), 
				CHAT | PARAM)
