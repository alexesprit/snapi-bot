# coding: utf-8

# io.py
# Initial Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os
import cPickle
import threading

smph = threading.BoundedSemaphore(1)

def _get_path(path):
	if not os.path.supports_unicode_filenames:
		path = path.encode("utf-8")
	dirname = os.path.dirname(path)
	if dirname and not os.path.exists(dirname):
		os.makedirs(dirname)
	return path

def get(path, mode="r"):
	path = _get_path(path)
	f = open(path, mode)
	return f
	
def read(path, default=None):
	path = _get_path(path)
	if not os.path.exists(path):
		if default is not None:
			open(path, "w").write(default)
		return default
	data = open(path, "r").read()
	return data.decode("utf-8")

def load(path, default=None):
	path = _get_path(path)
	if not os.path.exists(path):
		if default is not None:
			cPickle.dump(default, open(path, "wb"))
		return default
	return cPickle.load(open(path, "rb")) 

def write(path, data, mode="w"):
	if not isinstance(data, str):
		data = str(data)
	path = _get_path(path)
	with smph:
		open(path, mode).write(data)

def dump(path, data):
	path = _get_path(path)
	with smph:
		cPickle.dump(data, open(path, "wb"))
