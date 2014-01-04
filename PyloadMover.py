from module.plugins.Hook import Hook
import os
import shutil
import xml.etree.ElementTree as ET
import re
import traceback

	
class PyloadMover(Hook):
	"""
	Moves files to movie or series folder.
	"""
	__name__ = "PyloadMover"
	__version__ = "0.1"
	__description__ = "Moves finished downloads to movies or series folders."
	__config__ = [ ("activated" , "bool" , "Activated"  , "False" ),
		("movieSize" , "int" , "Treat files larger than this MB as movie"  , "-1" ),
		("moviesPath" , "str" , "Folder for movies"  , "/share/Multimedia/Movies" ),
		("seriesPath" , "str" , "Folder for series"  , "/share/Multimedia/Series" ), 
		("seriesMappingFile" , "str" , "XML File for mapping file names to series"  , "mover.xml" ),
		("deleteFolder" , "bool" , "Delete dowload folder after renaming"  , "True" ), ]
	#__threaded__ = ["downloadFinished"]
	__author_name__ = ("Paul Woelfel")
	__author_mail__ = ("pyload@frig.at")


	event_map = {"coreReady": "initialize",
		"unrarFinished":"unrarFinished",
		"pluginConfigChanged":"pluginConfigChanged"}

	activated = False
	movieSize = 2000
	moviesPath = None
	seriesPath = None
	seriesMappingFile = None
	deleteFolder = True

	videoFileEndings = ["mkv","avi"]

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

	"""
	initialize plugin
	"""
	def initialize(self):
		self.loadConfig()
		self.logDebug( "Initialized.")

	"""
	hook for finished unrar
	"""
	def unrarFinished(self,folder, fname):
		self.logInfo( "finished unrar of %s in %s" % (fname,folder))

		if self.activated:
			# we have to search folder for sub folders or files

			found = False
			# loop through directories in folder
			for (dirpath, dirnames, filenames) in os.walk(folder):
				# ignore samples
				if not ("sample" in dirpath.lower()):
					# search for videos in filenames
					for filename in filenames:
						fileEnding = self.getFileEnding(filename)

						if fileEnding in self.videoFileEndings:
							fullname=os.path.join(dirpath,filename)
							self.logInfo("found video %s %d" % (fullname,os.path.getsize(fullname)))
							found = True

							try:

								if self.movieSize > 0:
									if os.path.getsize(fullname) / (1024 * 1024) >= self.movieSize:
										# Movie
										self.logInfo("found movie")
										self.handleMovie(folder, dirpath, filename)
									else:
										# Series
										self.logInfo("found series")
										self.handleSeries(folder, dirpath, filename)

								else:
									# try as series first, otherwise treat as movie
									if not self.handleSeries( folder, dirpath, filename):
										self.logInfo("no series, try as movie")
										self.handleMovie( folder, dirpath, filename)

							except Exception, e:
								self.logError("failed to move or series file %s into folder: %s" % (fullname,e) )
								self.logError("Traceback %s" % traceback.format_exc(e))
							else:
								pass
							finally:
								pass


							break

				if found:
					break


	"""
	handle a series
	"""
	def handleSeries(self,folder,dirpath,filename):

		filenameLower=filename.lower()
		fullname=os.path.join(dirpath,filename)
		fileEnding=self.getFileEnding(filename)

		#search for mapping
		tree = ET.parse(self.seriesMappingFile)
		root = tree.getroot()

		foundMapping = False
		# go through all series nodes
		for series in root.getiterator("series"):

			# check mapping
			for mapping in series.getiterator("mapping"):
				if mapping.text.lower() in filenameLower:
					self.logInfo("mapping found %s for %s" % (mapping.text,series.get("name")))
					foundMapping = True
					# move element to series

					seriesFolderName = series.get("folder")
					if seriesFolderName == None:
						seriesFolderName = series.get("name")
						if seriesFolderName == None: 
							#again?
							self.logWarn("did not find a folder or name in series element")
							break
						seriesFolderName=seriesFolderName.replace(' ',".")


					seriesFolder=os.path.join(self.seriesPath,seriesFolderName)

					seasonNum = None
					episodeNum = None

					if re.match('.*S\.?(\d+)E\.?(\d+).*', filename,flags=re.IGNORECASE):
						m = re.search('.*S\.?(\d+)E\.?(\d+).*', filename,flags=re.IGNORECASE)
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


					if mapping.get("season"):
						# overide season mapping
						seasonNum=mapping.get("season")

					if len(seasonNum) == 1:
						seasonNum = "0%s"%(seasonNum)


					if len(episodeNum) == 1:
						episodeNum = "0%s"%(episodeNum)


					self.logInfo("Season: %s Episode: %s" %(seasonNum,episodeNum))

					seasonFolder = os.path.join(seriesFolder,"S.%s" % (seasonNum))

					if not os.path.isdir(seasonFolder):
						if os.path.isdir(os.path.join(seriesFolder,"S%s" % (seasonNum))):
							seasonFolder = os.path.join(seriesFolder,"S%s" % (seasonNum))
						else:
							# create folder
							os.makedirs(seasonFolder)

					self.logInfo("Season folder: %s" % (seasonFolder))

					destFilename = filename

					# optional: rename files
					if series.get("renamePattern") != None:
						destFilename=series.get("renamePattern").replace("%s",seasonNum).replace("%e",episodeNum).replace("%f",fileEnding)
					
					finalPath=os.path.join(seasonFolder,destFilename)
					self.logInfo("moving %s to %s"%(fullname,finalPath))
					shutil.move(fullname,finalPath)

					if self.deleteFolder:
						self.logInfo("removing folder %s" % (folder))
						shutil.rmtree(folder)

					return True

					break

			# break outer loop
			if foundMapping:
				break

		return False


	def handleMovie(self,folder,dirpath,filename):
		filenameLower=filename.lower()
		fullname=os.path.join(dirpath,filename)
		fileEnding=self.getFileEnding(filename)

		# create foldername out of filename (without file ending)
		folderName=os.path.join(self.moviesPath,filename.replace(".%s"%(fileEnding),""))
		
		self.logInfo("moving to %s " % (folderName))
		# create dirs
		os.makedirs(folderName)

		shutil.move(fullname,folderName)

		# delete downloaded folder if necesary
		if self.deleteFolder:
			self.logInfo("removing folder %s " % (folder))
			shutil.rmtree(folder)

		return True



	"""
	get the file ending of a filename
	"""
	def getFileEnding(self,filename):
		lastDot = filename.rfind(".")

		if lastDot == -1 or lastDot+1  == len(filename):
			# no file ending or dot at the end
			return None
		
		fileEnding = filename[lastDot+1 :].lower()

		return fileEnding


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
