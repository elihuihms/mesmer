import os.path
import shelve

def openUserPrefs( mode='r' ):
	home = os.path.expanduser("~")
	path = os.path.join( home, ".mesmer_prefs" )
	return shelve.open( path, mode )