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

def showBashOrgRu(type, conference, nick, param):
	if(param and param.isdigit()):
		req = 'http://bash.org.ru/quote/' + param;
	else:
		req = 'http://bash.org.ru/random';
	rawHtml = urllib.urlopen(req).read();
	items = re.search('<div class="q">.*?<div class="vote">.*?</div>.*?<div>(.*?)</div>.*?</div>', rawHtml, re.DOTALL);
	if(items):
		message = decode(items.group(1));
		sendMsg(type, conference, nick, unicode(message, 'cp1251'));
	else:
		sendMsg(type, conference, nick, u'не могу :(');

registerCommand(showBashOrgRu, u'бор', 10, u'Показывает случайную цитату из бора, Также можно вывести по заданному номеру', u'бор [номер]', (u'бор 223344', u'бор'));

def showBashOrgRuAbyss(type, conference, nick, param):
	rawHtml = urllib.urlopen('http://bash.org.ru/abysstop').read();
	#id = random.randrange(1, 26);
	#items = re.search('<b>%d:</b><div>(.*?)</div>' % (id), text, re.DOTALL);
	#quote = items.group(0);
	items = re.findall('<div>(.*?)</div>', rawHtml, re.DOTALL);
	if(items):
		message = random.choice(items);
		message = decode(message);
		sendMsg(type, conference, nick, unicode(message, 'cp1251'));
	else:
		sendMsg(type, conference, nick, u'не могу :(');

registerCommand(showBashOrgRuAbyss, u'борб', 10, u'Показывает случайную цитату из бездны бора', None, (u'борб', ), ANY | NONPARAM);

def showItHappens(type, conference, nick, param):
	rawHtml = urllib.urlopen('http://ithappens.ru/').read();
	idx = re.search('<h3><a href="/', rawHtml).end();
	rawHtml = rawHtml[idx:];
	idx = re.search('">', rawHtml).start();
	rawHtml = rawHtml[:idx];

	storyCount = rawHtml.split('/')[1];
	storyNum = random.randrange(1, int(storyCount));
	
	rawHtml = urllib.urlopen('http://ithappens.ru/story/%d' % (storyNum)).read();
	items = re.search('<p class="text">(.*?)</p>', rawHtml, re.DOTALL);
	if(items):
		text = decode(items.group(0));
		sendMsg(type, conference, nick, unicode(text, 'cp1251'));
	else:
		sendMsg(type, conference, nick, u'не могу');

registerCommand(showItHappens, u'ит', 10, u'Показывает случайную цитату c ithappens.ru', None, (u'ит', ), ANY | NONPARAM);
