# coding: utf-8

# clear.py
# Initial Copyright (c) Gigabyte <gigabyte@ngs.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CLEAR_ITERATIONS = 20

def clearConference(msgType, conference, nick, param):
	sendMsg(msgType, conference, nick, u"Сейчас уберу...")
	for i in xrange(CLEAR_ITERATIONS):
		sendToConference(conference, "")
		time.sleep(2)

registerCommand(clearConference, u"чисть", 15, 
				u"Очищает конференцию", 
				None, 
				None, 
				CHAT | NONPARAM)
