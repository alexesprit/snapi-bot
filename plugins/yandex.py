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

'''
<li>
<a href="http://tests.kulichki.com/" target="_blank"><b>Тесты</b>. Психологические <b>тесты</b> онлайн. Пройдите <b>тесты</b> бесплатно...</a><br/>
Самые правдивые и увлекательные <b>тесты</b> для Вас! Попробуйте, протестируйтесь! Все <b>тесты</b> абсолютно бесплатны и без регистрации.
<p class="b-phone">
</p>
<div class="www"><b>tests</b>.kulichki.com</div>
</li>

'''

def yandexSearch(type, conference, nick, param):
	query = urllib.urlencode({'query' : param.encode("utf-8")});
	text = urllib.urlopen('http://yandex.ru/msearch?s=all&%s' % (query)).read();
	items = re.findall('<li>(.*?)<div class="www">(.*?)</li>', text, re.DOTALL);
	if(items):
		if(PUBLIC == type):
			text = items[0][0].strip();
			url = items[0][1];
			message = u'%shttp://%s' % (text, url);
		else:
			items = [u'%shttp://%s' % (item[0].strip(), item[1]) for item in items[:5]];
			message = '\n'.join(items);
		message = message.replace('...', '');
		message = unicode(message, 'utf-8');
		sendMsg(type, conference, nick, decode(message));	
	else:
		sendMsg(type, conference, nick, u'По вашему запросу ничего не найдено');

registerCommandHandler(yandexSearch, u'яндекс', 10, u'Поиск в Яндексе', u'яндекс <запрос>', (u'яндекс google'), ANY | PARAM);
