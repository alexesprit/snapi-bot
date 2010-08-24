# coding: utf-8;

# updates.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showUpdates(type, conference, nick, param):
	changeList = [];
	for item in os.listdir(PLUGIN_DIR):
		changeTime = time.localtime(os.path.getctime(os.path.join(PLUGIN_DIR, item)));
		changeList.append(time.strftime('%Y-%m-%d: ' + item, changeTime));
	if(PUBLIC == type):
		sendMsg(type, conference, nick, u'скинула в приват');
	sendMsg(PRIVATE, conference, nick, u'что изменено:\n' + '\n'.join(changeList));

registerCommandHandler(showUpdates, u'изменения', 10, u'Даты изменений файлов в папке plugins', None, (u'изменения', ), ANY | NONPARAM);
