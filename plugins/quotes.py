# coding: utf-8

# quotes.py
# Initial Copyright (c) ???
# Modification Copyright (c) 2007 Als <Als@exploit.in>

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
		url = "http://bash.org.ru/quote/%s" % (param)
	else:
		url = "http://bash.org.ru/random"
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.search("quote/(\d+).+?<div>(.+?)</div>", rawhtml, re.DOTALL)
		if items:
			url = "http://bash.org.ru/quote/%s" % (items.group(1))
			quote = decode(items.group(2), "cp1251")
			sendMsg(msgType, conference, nick, "%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showAbyssQuote(msgType, conference, nick, param):
	url = "http://bash.org.ru/abysstop"
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.findall("<div class=\"vote\">(.+?)<div>(.+?)</div>", rawhtml, re.DOTALL)
		if items:
			items = [i[1] for i in items]
			rawquote = random.choice(items)
			message = decode(rawquote, "cp1251")
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
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.search(r"<div class.+?#(\d+).+?<p class=\"text\">(.+?)</p>", rawhtml, re.DOTALL)
		if items:
			url = "http://ithappens.ru/story/%s/" % (items.group(1))
			quote = decode(items.group(2), "cp1251")
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
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.search(r"<b>#(\d+).+?<div class=\"quotbody\">(.+?)</div>", rawhtml, re.DOTALL)
		if items:
			url = "http://ibash.org.ru/quote.php?id=%s" % (items.group(1))
			quote = decode(items.group(2), "cp1251")
			sendMsg(msgType, conference, nick, "%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showJabberQuote(msgType, conference, nick, param):
	if param and param.isdigit():
		url = "http://jabber-quotes.ru/id%s" % (param)
	else:
		url = "http://jabber-quotes.ru/random"
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.search(r"#(\d+).+?<blockquote>(.+?)</blockquote>", rawhtml)
		if items:
			quote = unicode(items.group(2), "cp1251")
			quote = quote.replace("<br><br>", "\n")
			quote = decode(quote)
			url = "http://jabber-quotes.ru/id%s/" % (items.group(1))
			sendMsg(msgType, conference, nick, u"%s\n\n%s" % (quote, url))
		else:
			sendMsg(msgType, conference, nick, u"Цитата не найдена!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showCinemaQuote(msgType, conference, nick, param):
	pageNum = random.randrange(1, 39)
	url = "http://skio.ru/afofilms/kino%d.php" % (pageNum)
	responce = getURL(url)
	if responce:
		rawhtml = responce.read()
		items = re.search("<ul type=\"circle\"(.+?)</ul>", rawhtml, re.DOTALL)
		if items:
			rawhtml = items.group(1)
			items = re.findall("<li>(.+?)<li>", rawhtml, re.DOTALL)
			quote = random.choice(items)
			quote = decode(quote, "cp1251")
			sendMsg(msgType, conference, nick, quote)
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showAbyssQuote, u"борб", 10, 
				u"Показывает случайную цитату из бездны bash.org.ru", 
				None, 
				(u"борб", ), 
				ANY | NONPARAM)
registerCommand(showBashQuote, u"бор", 10, 
				u"Показывает случайную/указанную цитату c bash.org.ru", 
				u"бор [номер]", 
				(u"бор", u"бор 143498"))
registerCommand(showIBashQuote, u"айбаш", 10, 
				u"Показывает случайную/указанную цитату c ibash.org.ru", 
				u"айбаш [номер]", 
				(u"айбаш", u"айбаш 3619"))
registerCommand(showItHappensQuote, u"ит", 10, 
				u"Показывает случайную/указанную цитату c ithappens.ru", 
				u"ит [номер]", 
				(u"ит", u"ит 2691"))
registerCommand(showJabberQuote, u"жк", 10, 
				u"Показывает случайную/указанную цитату с jabber-quotes.ru", 
				u"жк [номер]", 
				(u"жк", u"жк 204"));
registerCommand(showCinemaQuote, u"киноцитата", 10, 
				u"Показывает случайную цитату из кино", 
				None, 
				(u"киноцитата", ), 
				ANY | NONPARAM)