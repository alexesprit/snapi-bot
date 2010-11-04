# coding: utf-8

# anecdote.py
# Initial Copyright (c) Gigabyte <gigabyte@ngs.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showAnecdote(msgType, conference, nick, param):
	url = "http://anekdot.odessa.ua/rand-anekdot.php"
	rawHTML = urllib.urlopen(url).read()
	items = re.search("color:#FFFFFF'>(.+?)<a href", rawHTML, re.DOTALL)
	if items:
		rawtext = items.group(1).replace("<br />", "")
		anecdote = decode(rawtext, "cp1251")
		sendMsg(msgType, conference, nick, anecdote)
	else:
		sendMsg(msgType, conference, nick, u"Не получается")

registerCommand(showAnecdote, u"анекдот", 10, 
				u"Показывает случайный анекдот", 
				None, 
				(u"анекдот", ), 
				ANY | NONPARAM)
