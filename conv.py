import os
from module import database, io

def convert_db(dir, dbname):
	try:
		olddbpath = r"%s/%s.txt" % (dir, dbname)
		oldtimepath = r"%s/%s.txt.db" % (dir, dbname)
		
		if not os.path.exists(olddbpath):
			print "not found: %s" % (olddbpath)
			return
			
		print "convert db %s" % (dbname)

		newdbpath = r"%s/%s.dat" % (dir, dbname)
		newtimepath = r"%s/%s.dat.db" % (dir, dbname)

		data = eval(io.read(olddbpath, "{}"))
		time = eval(io.read(oldtimepath, "{}"))
		
		io.dump(newdbpath, data)
		io.dump(newtimepath, time)
		os.remove(olddbpath)
		os.remove(oldtimepath)
	except IOError:
		print "not found"

def convert_txt(dir, dbname):
	try:
		oldpath = r"%s/%s.txt" % (dir, dbname)
		if not os.path.exists(oldpath):
			print "not found: %s" % (oldpath)
			return
			
		print "convert txt %s" % (dbname)
		
		newpath = r"%s/%s.dat" % (dir, dbname)
		
		data = eval(io.read(oldpath))
		if '' in data:
			print "empty key"
			del data['']
		io.dump(newpath, data)
		os.remove(oldpath)
	except IOError:
		print "not found"
	
def merge_autoroles(dir):
	

	db1path = r"%s/moderators.txt" % (dir)
	db2path = r"%s/visitors.txt" % (dir)
	
	if not (os.path.exists(db1path) or os.path.exists(db2path)):
		return

	print "merge"

	dbnewpath = r"%s/autoroles.dat" % (dir)
	
	data1 = eval(io.read(db1path))
	data2 = eval(io.read(db2path))
	
	data = {}
	for k in data1:
		data[k] = "moder"
	for k in data1:
		data[k] = "visitor"
	io.dump(dbnewpath, data)
	os.remove(db1path)
	os.remove(db2path)

dirs = os.listdir("config")
for d in dirs:
	if os.path.isfile(r"config/%s" % (d)):
		continue

	convert_db(r"config/%s" % (d), "clients")
	convert_db(r"config/%s" % (d), "quiz")
	convert_db(r"config/%s" % (d), "seen")
	convert_db(r"config/%s" % (d), "send")
	convert_db(r"config/%s" % (d), "talkers")
	convert_db(r"config/%s" % (d), "tuta")
	
	convert_txt(r"config/%s" % (d), "access")
	convert_txt(r"config/%s" % (d), "cmdoff")
	convert_txt(r"config/%s" % (d), "config")
	convert_txt(r"config/%s" % (d), "greets")
	convert_txt(r"config/%s" % (d), "issues")
	convert_txt(r"config/%s" % (d), "localdb")
	convert_txt(r"config/%s" % (d), "macros")
	convert_txt(r"config/%s" % (d), "macrosaccess")
	convert_txt(r"config/%s" % (d), "record")
	convert_txt(r"config/%s" % (d), "votes")
	
	merge_autoroles(r"config/%s" % (d))

convert_txt(r"config", r"access")
convert_txt(r"config", r"notepad")
convert_txt(r"config", r"macros")
convert_txt(r"config", r"macrosaccess")
convert_txt(r"config", r"rosterstatus")