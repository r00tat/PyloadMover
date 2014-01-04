from module.plugins.Hook import Hook
import os
import shutil
import xml.etree.ElementTree as ET
import re

	
class PyloadMover(Hook):
	"""
	Moves files to movie or series folder.
	"""
	__name__ = "PyloadMover"
	__version__ = "0.1"
	__description__ = "Moves finished downloads to movies or series folders."
	__config__ = [ ("activated" , "bool" , "Activated"  , "False" ),
		("movieSize" , "int" , "Treat files larger than this MB as movie"  , "2000" ),
		("moviesPath" , "str" , "Folder for movies"  , "/share/Multimedia/Movies" ),
		("seriesPath" , "str" , "Folder for series"  , "/share/Multimedia/Series" ), 
		("seriesMappingFile" , "str" , "XML File for mapping file names to series"  , "mover.xml" ), ]
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
	seriesMappingFile = None

	"""
	load all config vars
	"""
	def loadConfig(self):
		self.activated=self.getConfig("activated")
		self.movieSize=self.getConfig("movieSize")
		self.moviesPath=self.getConfig("moviesPath")
		self.seriesPath=self.getConfig("seriesPath")
		self.seriesMappingFile=self.getConfig("seriesMappingFile")
		self.initSeriesMapping()

	"""
	initialize plugin
	"""
	def initialize(self):
		self.loadConfig()
		self.logDebug( "Initialized.")

	"""
	hook for finished downloads
	"""
	def downloadFinished(self, pyfile):
		self.logInfo( "download complete: %s" % (pyfile))


	"""
	hook for finished unrar
	"""
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

						if os.path.getsize(fullname) / (1024 * 1024) >= self.movieSize:
							self.logInfo("found movie")
							folderName=os.path.join(self.moviesPath,filename.replace(".mkv","").replace(".avi",""))
							self.logInfo("moving to %s " % (folderName))
							os.makedirs(folderName)

							shutil.move(fullname,folderName)

							self.logInfo("removing folder")
							shutil.rmtree(folder)


						else:
							self.logInfo("found series")

							try:
								#search for mapping
								tree = ET.parse(self.seriesMappingFile)
								root = tree.getroot()

								foundMapping = False
								for series in root.iter("series"):
									for mapping in series.iter("mapping"):
										if mapping.text in filename:
											self.logInfo("mapping found %s for %s" % (mapping.text,series.get("name")))
											foundMapping = True
											# move element to series

											seriesFolder=os.path.join(self.seriesPath,series.get("path"))

											seasonNum = None
											episodeNum = None

											if re.match('.*S\.?(\d+)E\.?(\d+).*', filename):
												m = re.search('.*S\.?(\d+)E\.?(\d+).*', filename)
												# found best match
												seasonNum = m.group(1)
												episodeNum = m.group(2)
											elif re.match('.*(\d+)(\d\d).*', filename):
												# not so a good match
												m = re.search('.*(\d+)(\d\d).*', filename)
												
												seasonNum = m.group(1)
												episodeNum = m.group(2)
											elif re.match('.*(\d\d).*', filename):
												# last guess
												m = re.search('.*(\d\d).*', filename)
												seasonNum = "01"
												episodeNum = m.group(1)
											elif re.match('.*(\d+).*', filename):
												# find any number in filename
												m = re.search('.*(\d+).*', filename)
												seasonNum = "01"
												episodeNum = m.group(1)
											else:
												# no episodeNum found
												seasonNum = "01"
												episodeNum = "01"


											self.logInfo("Season: %s Episode: %s" %(seasonNum,episodeNum))

											seasonFolder = os.path.join(seriesFolder,"S.%s" % (seasonNum))

											if not os.path.isdir(seasonFolder):
												if os.path.isdir(os.path.join(seriesFolder,"S%s" % (seasonNum))):
													seasonFolder = os.path.join(seriesFolder,"S%s" % (seasonNum))
												else:
													# create folder
													os.makedirs(seasonFolder)

											self.logInfo("Season folde: %s" % (seasonFolder))
											
											shutil.move(fullname,seasonFolder)

											self.logInfo("removing folder")
											shutil.rmtree(folder)


											break

									# break outer loop
									if foundMapping:
										break


							except Exception, e:
								self.logError("failed to move file into series folder: %s" % (e) )
							else:
								pass
							finally:
								pass



						break

			if found:
				break


	"""
	check if XML exists
	if not, create dummy mappings
	"""
	def initSeriesMapping(self):
		if not os.path.isfile(self.seriesMappingFile):
			# create root element
			root = ET.Element("mappings")

			# add a series
			series = ET.SubElement(root, "series")
			series.set("name","Some series title")
			series.set("folder","My.Series.Folder")

			# create mappings
			mapping = ET.SubElement(series, "mapping")
			mapping.text="someseries"

			mapping = ET.SubElement(series, "mapping")
			mapping.text="some.series"

			mapping = ET.SubElement(series, "mapping")
			mapping.text="my.series"

			tree = ET.ElementTree(root)
			tree.write(self.seriesMappingFile,"utf-8")
			
		else:
			try:
				tree = ET.parse(self.seriesMappingFile)
				root = tree.getroot()
				pass
			except Exception, e:
				# file is wrong
				self.logError("could not load mapping file %s: %s" % (self.seriesMappingFile, e))
			else:
				pass
			finally:
				pass
			

		
	"""
	hook for plugin Config changed
	"""
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
		elif param == "seriesMappingFile":
			self.seriesMappingFile=value
			self.initSeriesMapping()

		#self.loadConfig()
