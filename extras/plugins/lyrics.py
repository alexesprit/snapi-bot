# coding: utf-8

# lyrics.py
# Initial Copyright (c) 2010 -Esprit-

# Поиск слов песен на pesenki.ru.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getLyricsFromURL(url):
	response = getURL(url)
	if response:
		rawhtml = response.read()
		rawtext = re.search(r"<div class=text>.+?<font>(.+?)</font>", rawhtml, re.DOTALL)
		rawtext = rawtext.group(1).replace("<br />", "")	 
		
		songtext = decode(rawtext).strip()
		return songtext 
	else:
		return None

def searchForLyrics(msgType, conference, nick, param):
	args = param.split(None, 1)
	number = 0
	search = param
	if 2 == len(args):
		if args[0].isdigit():
			number = int(args[0])
			search = args[1]
	
	mainurl = "http://pesenki.ru"
	url = "%s/search.shtml" % (mainurl)
	qparam = {
		"t": "song",
		"q": search.encode("utf-8")
	}
	response = getURL(url, qparam)
	if response:
		rawhtml = response.read()
		rawhtml = unicode(rawhtml, "cp1251")

		elements = re.findall(r"<a href=\".+?\">(.+?)</a>.+?<a href=\"(.+?)\"><b class=.+?>(.+?)</b>(.+?)</a>", rawhtml)
		if elements:
			if 1 == len(elements) or number:
				if number:
					try:
						element = elements[number - 1]
					except IndexError:
						sendMsg(msgType, conference, nick, u"Ошибка! Элемент не найден")
						return
				else:
					element = elements[0]
				artist = element[0]
				title = element[3]
				url = u"%s%s" % (mainurl, element[1])
				result = u"%s -%s\n\n%s" % (artist, title, getLyricsFromURL(url))			
			else:
				songs = []
				for i, element in enumerate(elements):
					artist = element[0]
					title = element[3]
					stype = element[2]
					page = element[1]
					songs.append(u"%d) %s -%s (%s)\n%s%s" % (i + 1, artist, title, stype, mainurl, page))
				result = "\n".join(songs)
			message = u"Вот, что я нашла:\n%s" % (result)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(searchForLyrics, u"lyrics", 10, 
				u"Ищет тексты песен на pesenki.ru. Если найдено более одной песни, то покажет список найденных песен (для показа слов нужной Вам песни из списка нужно указать номер песни перед названием)",
				u"[номер] <название>", 
				(u"Skin Deep", u"7 Skin Deep"), 
				CMD_ANY | CMD_PARAM)
