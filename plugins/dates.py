# coding: utf-8;

# dates.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showDates(type, conference, nick, param):
	rawHtml = urllib.urlopen('http://wap.n-urengoy.ru/cgi-bin/wappr.pl').read();
	rawHtml = unicode(rawHtml, 'utf-8');
	dates = rawHtml.split('<br/>-----<br/>');
	dates = dates[1:-1];
	if(dates):
		dates = [x.split('/')[0] for x in dates];
		sendMsg(type, conference, nick, u'глянь, что я нашла:' + u'\n'.join(dates));
	else:
		sendMsg(type, conference, nick, u'ничего не нашла :(');

registerCommand(showDates, u'праздники', 10, u'Показывает праздники на сегодня и завтра', None, (u'праздники', ));
