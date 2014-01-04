from module.plugins.Hook import Hook

class PyloadMover(Hook):
	"""
    Moves files to movie or series folder.
    """
    __name__ = "PyloadMover"
    __version__ = "0.1"
    __description__ = "Moves finished downloads to movies or series folders."
    __config__ = [ ("activated" , "bool" , "Activated"  , "True" ),
    	("movieSize" , "int" , "Treat files larger than this MB as movie"  , "2000" ),
    	("moviesPath" , "str" , "Folder for movies"  , "/share/Multimedia/Filme" ),
    	("seriesPath" , "str" , "Folder for series"  , "/share/Multimedia/Serien" ), ]
    #__threaded__ = ["downloadFinished"]
    __author_name__ = ("Paul Woelfel")
    __author_mail__ = ("pyload@frig.at")


	event_map = {"downloadFinished" : "downloadFinished",
		"coreReady": "initialize",
		"unrarFinished":"unrarFinished",
		"pluginConfigChanged":"pluginConfigChanged"}

	def initialize(self):
		print "Initialized."

	def downloadFinished(self, pyfile):
		print "download complete: %s".format(pyfile)

	def unrarFinished(self,folder, fname):
		print "finished unrar of %s in %s".format(fname,folder)

	def pluginConfigChanged(self):
		print "Plugin config changed!"
	