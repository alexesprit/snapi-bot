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

TYPE_DIR = 1;
TYPE_FILE = 2;
		
def deleteFromConfig(msgType, conference, nick, param):
	files, dirs = 0, 0;
	for conf in getConferences():
		path = getConfigPath(conf, param);
		answer = deleteFile(path);
		if(TYPE_DIR == answer):
			dirs += 1;
		elif(TYPE_FILE == answer):
			files += 1;
	sendMsg(msgType, conference, nick, u'удалено %d папок и %d файлов' % (dirs, files));
	
def deleteFile(path):
	if(os.path.exists(path)):
		if(os.path.isdir(path)):
			shutil.rmtree(path);
			return(TYPE_DIR);
		else:
			os.remove(path);
			return(TYPE_FILE);
	else:
		return(-1);

registerCommand(deleteFromConfig, u'rmcfg', 100, u'Удаляет файл или папку из /config', u'rmcfg <имя>', (u'rmcfg test.txt', ), ROSTER | PARAM);	 
