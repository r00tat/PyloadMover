from module.plugins.Hook import Hook
import os
import shutil
import xml.etree.ElementTree as ET
import re
import traceback
from Mover import Mover 

	
class PyloadMover(Hook,Mover):
	"""
	Moves files to movie or series folder.
	"""
	__name__ = "PyloadMover"
	__version__ = "0.2"
	__description__ = "Moves finished downloads to movies or series folders."
	__config__ = [ ("activated" , "bool" , "Activated"  , "False" ),
		("movieSize" , "int" , "Treat files larger than this MB as movie"  , "-1" ),
		("moviesPath" , "str" , "Folder for movies"  , "/share/Multimedia/Movies" ),
		("seriesPath" , "str" , "Folder for series"  , "/share/Multimedia/Series" ), 
		("seriesMappingFile" , "str" , "XML File for mapping file names to series"  , "mover.xml" ),
		("deleteFolder" , "bool" , "Delete dowload folder after renaming"  , "True" ), ]
	#__threaded__ = ["downloadFinished"]
	__author_name__ = ("r00tat")
	__author_mail__ = ("pyload@frig.at")


	event_map = {"coreReady": "initialize",
		"unrarFinished":"unrarFinished",
		"pluginConfigChanged":"pluginConfigChanged"}

	

	"""
	load all config vars
	"""
	def loadConfig(self):
		self.activated=self.getConfig("activated")
		self.movieSize=self.getConfig("movieSize")
		self.moviesPath=self.getConfig("moviesPath")
		self.seriesPath=self.getConfig("seriesPath")
		self.seriesMappingFile=self.getConfig("seriesMappingFile")
		self.deleteFolder=self.getConfig("deleteFolder")
		self.initSeriesMapping()
		self.logInfo("PyloadMover loaded.")

		
	"""
	hook for plugin Config changed
	"""
	def pluginConfigChanged(self,moduleName,param,value):
		if moduleName == "PyloadMover":
			self.logInfo( "Plugin config changed: %s=%s" % (param,value))
			if param == "activated":
				self.activated=value
			elif param == "movieSize":
				self.movieSize=value
			elif param == "moviePath":
				self.moviesPath=value
			elif param == "seriesPath":
				self.seriesPath = value
			elif param == "seriesMappingFile":
				self.seriesMappingFile=value
				self.initSeriesMapping()
			elif param == "deleteFolder":
				self.deleteFolder=value

		#self.loadConfig()


	def debug(self,message):
		self.logDebug(message)

	def info(self,message):
		self.logInfo(message)

	def warn(self,message):
		self.logWarn(message)

	def err(self,message):
		self.logError(message)

