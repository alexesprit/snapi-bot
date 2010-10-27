# coding: utf-8

# facts.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

FACTS_COUNT = 28

def showFact(msgType, conference, nick, param):
	pageNum = random.randrange(1, FACTS_COUNT + 1)
	url = "http://skio.ru/facts/fact%d.php" % (pageNum)
	rawHTML = urllib.urlopen(url).read()
	items = re.search("<div style=.+?<ul>(.+?)</ul>", rawHTML, re.DOTALL)
	if(items):
		rawHTML = items.group(1)
		items = re.findall("<li>(.+?)</li>", rawHTML, re.DOTALL)
		fact = random.choice(items)
		fact = decode(fact)
		sendMsg(msgType, conference, nick, unicode(fact, "cp1251"))
	else:
		sendMsg(msgType, conference, nick, u"не получается")

registerCommand(showFact, u"факт", 10, 
				u"Показывает случайный интересный факт", 
				None, 
				(u"факт", ), 
				ANY | NONPARAM)
