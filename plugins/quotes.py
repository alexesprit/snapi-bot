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
	if(param and param.isdigit()):
		req = "http://bash.org.ru/quote/%s" % (param)
	else:
		req = "http://bash.org.ru/random"
	rawHTML = urllib.urlopen(req).read()
	items = re.search("<div class=\"vote\">(.+?)<div>(.+?)</div>", rawHTML, re.DOTALL)
	if(items):
		message = decode(items.group(2))
		sendMsg(msgType, conference, nick, unicode(message, "cp1251"))
	else:
		sendMsg(msgType, conference, nick, u"не могу :(")

def showAbyssQuote(msgType, conference, nick, param):
	rawHTML = urllib.urlopen("http://bash.org.ru/abysstop").read()
	items = re.findall("<div class=\"vote\">(.+?)<div>(.+?)</div>", rawHTML, re.DOTALL)
	if(items):
		items = [i[1] for i in items]
		message = random.choice(items)
		message = decode(message)
		sendMsg(msgType, conference, nick, unicode(message, "cp1251"))
	else:
		sendMsg(msgType, conference, nick, u"не могу :(")

def showItHappensQuote(msgType, conference, nick, param):
	if(param and param.isdigit()):
		url = "http://ithappens.ru/%s" % (param)
	else:
		url = "http://ithappens.ru/random"
	rawHTML = urllib.urlopen(url).read()
	items = re.search(r"<p class=\"text\">(.+?)</p>", rawHTML, re.DOTALL)
	if(items):
		text = decode(items.group(0))
		sendMsg(msgType, conference, nick, unicode(text, "cp1251"))
	else:
		sendMsg(msgType, conference, nick, u"не могу")

def showJabberQuote(msgType, conference, nick, param):
	if(param and param.isdigit()):
		url = "http://jabber-quotes.ru/id%s" % (param)
	else:
		url = "http://jabber-quotes.ru/random"
	rawHTML = urllib.urlopen(url).read()
	items = re.findall(r"<blockquote>(.*?)</blockquote>", rawHTML)
	if(items):
		message = random.choice(items)
		message = message.replace("<br><br>", "<br>")
		message = decode(message)
		message = unicode(message, "cp1251")
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"не могу :(")

registerCommand(showAbyssQuote, u"борб", 10, 
				u"Показывает случайную цитату из бездны bash.org.ru", 
				None, 
				(u"борб", ), 
				ANY | NONPARAM)
registerCommand(showBashQuote, u"бор", 10, 
				u"Показывает случайную/указанную цитату c bash.org.ru", 
				u"бор [номер]", 
				(u"бор", u"бор 143498"))
registerCommand(showItHappensQuote, u"ит", 10, 
				u"Показывает случайную/указанную цитату c ithappens.ru", 
				u"ит [номер]", 
				(u"ит", u"ит 2691"))
registerCommand(showJabberQuote, u"жк", 10, 
				u"Показывает случайную/указанную цитату с jabber-quotes.ru", 
				u"жк [номер]", 
				(u"жк", u"жк 204"));
