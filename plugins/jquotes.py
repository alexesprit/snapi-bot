# coding: utf-8;

# jquotes.py 
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

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

registerCommand(showJQuote, u"жк", 10, u"Цитаты с jabber-quotes.ru", None, (u"жк", ), ANY | NONPARAM);
