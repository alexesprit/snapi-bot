# coding: utf-8

# quotes.py
# Initial Copyright (c) ???
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showBashQuote(msgType, conference, nick, param):
	if param and param.isdigit():
		url = "http://bash.im/quote/%s" % (param)
	else:
		url = "http://bash.im/random"
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.search(r"link: '(.+?)'.+?<div class=\"text\">(.+?)</div>", data, re.DOTALL)
		if elements:
			url = elements.group(1)
			quote = netutil.removeTags(elements.group(2))
			sendMsg(msgType, conference, nick, "%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showAbyssQuote(msgType, conference, nick, param):
	url = "http://bash.im/abysstop"
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.findall("<div class=\"text\">(.+?)</div>", data, re.DOTALL)
		if elements:
			rawquote = random.choice(elements)
			message = netutil.removeTags(rawquote)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showItHappensQuote(msgType, conference, nick, param):
	if param and param.isdigit():
		url = "http://ithappens.ru/story/%s" % (param)
	else:
		url = "http://ithappens.ru/random"
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.search(r"<p class=\"text\" id=\"story_(.+?)\">(.+?)</p>", data, re.DOTALL)
		if elements:
			url = "http://ithappens.ru/story/%s" % (elements.group(1))
			quote = netutil.removeTags(elements.group(2))
			sendMsg(msgType, conference, nick, "%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showIBashQuote(msgType, conference, nick, param):
	if param and param.isdigit():
		url = "http://ibash.org.ru/quote.php?id=%s" % (param)
	else:
		url = "http://ibash.org.ru/random.php"
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.search(r"<b>#(\d+).+?<div class=\"quotbody\">(.+?)</div>", data, re.DOTALL)
		if elements:
			url = "http://ibash.org.ru/quote.php?id=%s" % (elements.group(1))
			quote = netutil.removeTags(elements.group(2))
			sendMsg(msgType, conference, nick, "%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showJabberQuote(msgType, conference, nick, param):
	if param and param.isdigit():
		url = "http://jabber-quotes.ru/api/read/?id=%s" % (param)
	else:
		url = "http://jabber-quotes.ru/api/read/?id=random"
	data = netutil.getURLResponseData(url, encoding='raw')
	if data:
		xmlnode = simplexml.XML2Node(data)

		quote = xmlnode.getTagData("quote")
		if quote:
			id = xmlnode.getTagData("id")
			url = "http://jabber-quotes.ru/id/%s" % (id)
			sendMsg(msgType, conference, nick, u"%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showCinemaQuote(msgType, conference, nick, param):
	pageNum = random.randrange(1, 39)
	url = "http://skio.ru/afofilms/kino%d.php" % (pageNum)
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.search("<ul type=\"circle\"(.+?)</ul>", data, re.DOTALL)
		if elements:
			rawhtml = elements.group(1)
			elements = re.findall("<li>(.+?)<li>", rawhtml, re.DOTALL)
			quote = random.choice(elements)
			quote = netutil.removeTags(quote)
			sendMsg(msgType, conference, nick, quote)
		else:
			sendMsg(msgType, conference, nick, u"Нет цитат!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showFact(msgType, conference, nick, param):
	pageNum = random.randrange(1, 29)
	url = "http://skio.ru/facts/fact%d.php" % (pageNum)
	data = netutil.getURLResponseData(url)
	if data:
		elements = re.findall("<li>(.+?)<br><br></li>", data)
		if elements:
			fact = random.choice(elements)
			sendMsg(msgType, conference, nick, netutil.removeTags(fact))
		else:
			sendMsg(msgType, conference, nick, u"Нет фактов!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showAnecdote(msgType, conference, nick, param):
	url = "http://anekdot.odessa.ua/rand-anekdot.php"
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.search("color:#FFFFFF'>(.+?)<a href", data, re.DOTALL)
		if elements:
			rawtext = elements.group(1).replace("<br />", "")
			anecdote = netutil.removeTags(rawtext)
			sendMsg(msgType, conference, nick, anecdote)
		else:
			sendMsg(msgType, conference, nick, u"Нет анекдота!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")		

def showAforism(msgType, conference, nick, param):
	randPage = random.choice((
		"biz_quotes.php",
		"rich_quotes.php",
		"family_quotes.php",
		"kids_quotes.php",
		"friend_quotes.php",
		"human_quotes.php",
		"health_quotes.php",
		"beauty_quotes.php",
		"love_quotes.php",
		"world_quotes.php",
		"wisdom_quotes.php",
		"menwomen_quotes.php",
		"science_quotes.php",
		"edu_quotes.php",
		"pessimism_quotes.php",
		"politics_quotes.php",
		"truth_quotes.php",
		"religion_quotes.php",
		"death_quotes.php",
		"happy_quotes.php",
		"work_quotes.php",
		"humour_quotes.php"))
	url = "http://skio.ru/quotes/%s" % (randPage)
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.search("<p><div align=\"center\">(.+?)</div>", data, re.DOTALL)
		if elements:
			aforism = elements.group(1)
			sendMsg(msgType, conference, nick, aforism)
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")		

def showAdvert(msgType, conference, nick, param):
	pageNum = random.randrange(1, 13)
	url = "http://skio.ru/funnyad/%d.php" % (pageNum)
	data = netutil.getURLResponseData(url, encoding='windows-1251')
	if data:
		elements = re.findall(r"<tr><td>(.+?)</td></tr>", data, re.DOTALL)
		if elements:
			adv = random.choice(elements)
			sendMsg(msgType, conference, nick, netutil.removeTags(adv))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")		

registerCommand(showAbyssQuote, u"борб", 10, 
				u"Показывает случайную цитату из бездны bash.org.ru", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
registerCommand(showBashQuote, u"бор", 10, 
				u"Показывает случайную/указанную цитату c bash.org.ru", 
				u"[номер]", 
				(None, u"143498"))
registerCommand(showIBashQuote, u"айбаш", 10, 
				u"Показывает случайную/указанную цитату c ibash.org.ru", 
				u"[номер]", 
				(None, u"3619"))
registerCommand(showItHappensQuote, u"ит", 10, 
				u"Показывает случайную/указанную цитату c ithappens.ru", 
				u"[номер]", 
				(None, u"2691"))
registerCommand(showJabberQuote, u"жк", 10, 
				u"Показывает случайную/указанную цитату с jabber-quotes.ru", 
				u"[номер]", 
				(None, u"204"))
registerCommand(showCinemaQuote, u"киноцитата", 10, 
				u"Показывает случайную цитату из кино", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
registerCommand(showFact, u"факт", 10, 
				u"Показывает случайный интересный факт", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
registerCommand(showAforism, u"афор", 10, 
				u"Показывает случайный афоризм", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
registerCommand(showAnecdote, u"анекдот", 10, 
				u"Показывает случайный анекдот", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
registerCommand(showAdvert, u"объявление", 10, 
				u"Показывает случайное интересное объявление", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)