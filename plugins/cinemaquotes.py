# coding: utf-8

# cinemauotes.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

CINEMAQUOTES_COUNT = 38

def showCinemaQuote(msgType, conference, nick, param):
	pageNum = random.randrange(1, CINEMAQUOTES_COUNT + 1)
	url = "http://skio.ru/afofilms/kino%d.php" % (pageNum)
	rawHTML = urllib.urlopen(url).read()
	items = re.search("<ul type=\"circle\"(.+?)</ul>", rawHTML, re.DOTALL)
	if(items):
		rawHTML = items.group(0)
		items = re.findall("<li>(.+?)<li>", rawHTML, re.DOTALL)
		if not items:
			print pageNum
		quote = random.choice(items)
		quote = decode(quote)
		sendMsg(msgType, conference, nick, unicode(quote, "cp1251"))
	else:
		sendMsg(msgType, conference, nick, u"не получается")

registerCommand(showCinemaQuote, u"киноцитата", 10, 
				u"Показывает случайную цитату из кино", 
				None, 
				(u"киноцитата", ), 
				ANY | NONPARAM)
