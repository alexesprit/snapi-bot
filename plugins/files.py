# coding: utf-8;

# files.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import shutil;

DIR = 1;
FILE = 2;

def showDirectory(type, conference, nick, param):
	if(os.path.exists(param)):
		if(os.path.isdir(param)):
			items = os.listdir(param);
			if(items):
				content = [];
				text = u'содержимое %s:\n' % (param);
				for item in items:
					if(os.path.isdir(os.path.join(param, item))):
						content.append('/%s' % (item));
					else:
						content.append(item);
				content.sort();
				text += '\n'.join(content);
				sendMsg(type, conference, nick, text);
			else:
				sendMsg(type, conference, nick, u'папка пуста');
		else:
			sendMsg(type, conference, nick,	u'а это не папка :)');
	else:
		sendMsg(type, conference, nick,	u'не найдено');

def deletePath(type, conference, nick, param):
	answer = deleteFile(param);
	if(answer == DIR):
		sendMsg(type, conference, nick,	u'папка удалена');
	elif(answer == FILE):
		sendMsg(type, conference, nick,	u'файл удалён');
	else:
		sendMsg(type, conference, nick,	u'не найдено');
		
def deleteFromConfig(type, conference, nick, param):
	files, dirs = 0, 0;
	for conf in getChatList():
		path = 'config/%s/%s' % (conf, param);
		answer = deleteFile(path);
		if(answer == DIR):
			dirs += 1;
		elif(answer == FILE):
			files += 1;
	sendMsg(type, conference, nick, u'удалено %d папок и %d файлов' % (dirs, files));
	
def deleteFile(path):
	if(os.path.exists(path)):
		if(os.path.isdir(path)):
			shutil.rmtree(path);
			return(DIR);
		else:
			os.remove(path);
			return(FILE);
	else:
		return(-1);

registerCommandHandler(deleteFromConfig, u'rmcfg', 100, u'Удаляет файл или папку из /config', u'rmcfg <имя>', (u'rmcfg test.txt', ), ROSTER | PARAM);	 
registerCommandHandler(deletePath, u'rm', 100, u'Удаляет файл или папку', u'rm <имя>', (u'rm test.txt', ), ROSTER | PARAM);
registerCommandHandler(showDirectory, u'ls', 100, u'Показывает список указанного каталога', u'ls <путь>', (u'ls dynamic', ), ROSTER | PARAM);
