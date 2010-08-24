# coding: utf-8;

# svn.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

URLS = ('http://', 'https://', 'svn://');

def showSvnLog(type, conference, nick, param):
	if(param):
		for x in URLS:
			if(param.startswith(x)):
				param = param.split();
				if(len(param) == 2):
					try:
						count = int(param[1]);
					except(ValueError):
						sendMsg(type, conference, nick, u'прочитай помощь по команде');
						return;
				else:
					count = 10;
				url = param[0];
				pipe = os.popen('svn log %s --limit %d' % (url, count));
				sendMsg(type, conference, nick, pipe.read().decode('utf-8'));
				break;

registerCommandHandler(showSvnLog, u'svn', 10, u'Показывает лог с svn', u'svn <адрес> [кол-во]', (u'svn http://jimm-fork.googlecode.com/svn/trunk 5', ), ANY);
