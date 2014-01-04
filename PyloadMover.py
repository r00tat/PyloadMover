from module.plugins.Hook import Hook
import os
from os.path import join, getsize

	
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

	activated = False
	movieSize = 2000
	moviesPath = None
	seriesPath = None

	def loadConfig(self):
		self.activated=self.getConfig("activated")
		self.movieSize=self.getConfig("movieSize")
		self.moviesPath=self.getConfig("moviesPath")
		self.seriesPath=self.getConfig("seriesPath")

	def initialize(self):
		self.loadConfig()
		self.logDebug( "Initialized.")

	def downloadFinished(self, pyfile):
		self.logInfo( "download complete: %s" % (pyfile))

	def unrarFinished(self,folder, fname):
		self.logInfo( "finished unrar of %s in %s" % (fname,folder))

		# we have to search folder for sub folders or files

		found = False
		# loop through directories in folder
		for (dirpath, dirnames, filenames) in os.walk(folder):
			# ignore samples
			if not (dirpath == "sample" or dirpath == "Sample"):
				# search for videos in filenames
				for filename in filenames:
					if filename.endswith(".mkv") or filename.endswith(".avi"):
						fullname=os.path.join(dirpath,filename)
						self.logInfo("found video %s %d" % (fullname,os.path.getsize(fullname)))
						found = True

						break

			if found:
				break

		

	def pluginConfigChanged(self,moduleName,param,value):
		self.logInfo( "Plugin config changed: %s=%s" % (param,value))
		if param == "activated":
			self.activated=value
		elif param == "movieSize":
			self.movieSize=value
		elif param == "moviePath":
			self.moviesPath=value
		elif param == "seriesPath":
			self.seriesPath = value
		#self.loadConfig()
