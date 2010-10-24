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

gAnecdotePattern = re.compile("<div style='color: #000000;(.+?)<a href='http://anekdot.odessa.ua/' target='_blank'>", re.DOTALL)

def showAnecdote(msgType, conference, nick, param):
	url = "http://anekdot.odessa.ua/rand-anekdot.php"
	rawHTML = urllib.urlopen(url).read()
	items = gAnecdotePattern.search(rawHTML)
	if(items):
		anecdote = decode(items.group(0), "cp1251")
		sendMsg(msgType, conference, nick, anecdote)
	else:
		sendMsg(msgType, conference, nick, u"не получается")

registerCommand(showAnecdote, u"анекдот", 10, 
				u"Показывает случайный анекдот", 
				None, 
				(u"анекдот", ), 
				ANY | NONPARAM)
