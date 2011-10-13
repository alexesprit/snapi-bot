# config.py

def load(path):
	global USERNAME, SERVER

	execfile(path, globals())
	USERNAME, SERVER = JID.split("@")
