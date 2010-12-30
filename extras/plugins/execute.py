# coding: utf-8;

# execute.py
# Initial Copyright (c) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

EXECUTE_FILE = "execute.txt"

def executeExternalCode():
	path = getConfigPath(EXECUTE_FILE)
	if os.path.exists(path):
		try:
			execfile(path, globals())
		except Exception:
			printf("Error while executing %s!" % (path), FLAG_ERROR)
			addTextToSysLog(traceback.format_exc(), LOG_ERRORS)
	else:
		addTextToSysLog("%s is not found!" % (path), LOG_WARNINGS, True)

registerEventHandler(executeExternalCode, EVT_STARTUP)
