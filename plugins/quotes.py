# coding: utf-8;

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

def showBashOrgRu(msgType, conference, nick, param):
	if(param and param.isdigit()):
		req = 'http://bash.org.ru/quote/' + param;
	else:
		req = 'http://bash.org.ru/random';
	rawHtml = urllib.urlopen(req).read();
	items = re.search('<div class="vote">(.+?)<div>(.+?)</div>', rawHtml, re.DOTALL);
	if(items):
		message = decode(items.group(2));
		sendMsg(msgType, conference, nick, unicode(message, 'cp1251'));
	else:
		sendMsg(msgType, conference, nick, u'не могу :(');

def showBashOrgRuAbyss(msgType, conference, nick, param):
	rawHtml = urllib.urlopen('http://bash.org.ru/abysstop').read();
	items = re.findall('<div class="vote">(.+?)<div>(.+?)</div>', rawHtml, re.DOTALL);
	if(items):
		items = [i[1] for i in items];
		message = random.choice(items);
		message = decode(message);
		sendMsg(msgType, conference, nick, unicode(message, 'cp1251'));
	else:
		sendMsg(msgType, conference, nick, u'не могу :(');

def showItHappens(msgType, conference, nick, param):
	if(param and param.isdigit()):
		url = "http://ithappens.ru/%s" % (param);
	else:
		url = "http://ithappens.ru/random";
	rawHtml = urllib.urlopen(url).read();
	items = re.search(r"<p class=\"text\">(.+?)</p>", rawHtml, re.DOTALL);
	if(items):
		text = decode(items.group(0));
		sendMsg(msgType, conference, nick, unicode(text, "cp1251"));
	else:
		sendMsg(msgType, conference, nick, u'не могу');

def showJQuote(msgType, conference, nick, param):
	url = "http://jabber-quotes.ru/random";
	rawHtml = urllib.urlopen(url).read();
	items = re.findall(r"<blockquote>(.*?)</blockquote>", rawHtml);
	if(items):
		message = random.choice(items);
		message = message.replace("<br><br>", "<br>");
		message = decode(message);
		message = unicode(message, "cp1251");
		sendMsg(msgType, conference, nick, message);
	else:
		sendMsg(msgType, conference, nick, u"не могу :(");

registerCommand(showBashOrgRu, u"бор", 10, u"Показывает случайную/указанную цитату c bash.org.ru", u"бор [номер]", (u"бор", u"бор 223344"));
registerCommand(showBashOrgRuAbyss, u"борб", 10, u"Показывает случайную цитату из бездны bash.org.ru", None, (u"борб", ), ANY | NONPARAM);
registerCommand(showItHappens, u"ит", 10, u"Показывает случайную/указанную цитату c ithappens.ru", None, (u"ит", ));
registerCommand(showJQuote, u"жк", 10, u"Показывает случайную с jabber-quotes.ru", None, (u"жк", ), ANY | NONPARAM);