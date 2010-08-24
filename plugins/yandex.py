# coding: utf-8;

# yandex.py
# Initial Copyright (c) ferym <ferym@jabbim.org.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def yandexSearch(type, conference, nick, param):
	query = urllib.urlencode({'query' : param.encode("utf-8")});
	rawHtml = urllib.urlopen('http://yandex.ru/msearch?s=all&%s' % (query)).read();
	rawHtml = unicode(rawHtml, 'utf-8');
	items = re.findall('<li>(.*?)<div class="www">(.*?)</li>', rawHtml, re.DOTALL);
	if(items):
		if(PUBLIC == type):
			text = items[0][0].strip();
			url = items[0][1];
			message = u'%shttp://%s' % (text, url);
		else:
			items = [u'%shttp://%s' % (item[0].strip(), item[1]) for item in items[:5]];
			message = '\n'.join(items);
		message = message.replace('...', '');
		sendMsg(type, conference, nick, decode(message));	
	else:
		sendMsg(type, conference, nick, u'По вашему запросу ничего не найдено');

registerCommandHandler(yandexSearch, u'яндекс', 10, u'Поиск в Яндексе', u'яндекс <запрос>', (u'яндекс google'), ANY | PARAM);
