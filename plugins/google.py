# coding: utf-8;

# google.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def google(msgType, conference, nick, text):
	query = urllib.urlencode({'q' : text.encode("utf-8")});
	url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&hl=ru&%s' % (query);
	googleSearch(msgType, conference, nick, url);

def googleEn(msgType, conference, nick, text):
	query = urllib.urlencode({'q' : text.encode("utf-8")});
	url = 'http://ajax.googleapis.com/ajax/services/search/web?hl=en&v=1.0&%s&lr=lang_en' % (query);
	googleSearch(msgType, conference, nick, url);

def googleRu(msgType, conference, nick, text):
	query = urllib.urlencode({'q' : text.encode("utf-8")});
	url = 'http://ajax.googleapis.com/ajax/services/search/web?hl=ru&v=1.0&%s&lr=lang_ru' % (query);
	googleSearch(msgType, conference, nick, url);

def googleSearch(msgType, conference, nick, url):
	req = urllib.urlopen(url);
	answer = simplejson.load(req);
	results = answer['responseData']['results'];
	if(results):
		if(msgType == PUBLIC):
			msg = ['%(title)s\n%(content)s\n%(unescapedUrl)s' % (results[0])];
		else:
			msg = ['%(title)s\n%(content)s\n%(unescapedUrl)s' % (result) for result in results];
		sendMsg(msgType, conference, nick, decode('\n\n'.join(msg)));
	else:
		sendMsg(msgType, conference, nick, u'не найдено');

registerCommand(googleEn, u'гугльен', 10, u'Поиск через Google, по буржуйским сайтам', u'гугльен <текст>', (u'гугльен yandex', ), ANY | PARAM);
registerCommand(googleRu, u'гугльру', 10, u'Поиск через Google, по нашим, русским сайтам', u'гугльру <текст>', (u'гугльру yandex', ), ANY | PARAM);
registerCommand(google, u'гугль', 10, u'Поиск через Google', u'гугль <текст>', (u'гугль yandex', ), ANY | PARAM);
