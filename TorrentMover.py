import os
import shutil
import xml.etree.ElementTree as ET
import re
import traceback
from Mover import Mover 
import logging
import sys

	
class TorrentMover(Mover):
	"""
	Moves files to movie or series folder.
	"""
	__name__ = "TorrentMover"
	__version__ = "0.2"
	__description__ = "Moves finished downloads to movies or series folders."
	__author_name__ = ("r00tat")
	__author_mail__ = ("pyload@frig.at")

	configFile = "config.xml"

	"""

	"""
	def __init__(self,confFile):
		self.configFile = confFile
		self.initialize()


	"""
	load all config vars
	"""
	def loadConfig(self):
		self.activated=True
		self.movieSize=0

		tree = ET.parse(self.configFile)
		root = tree.getroot()

		for child in root:
			if child.tag == "moviesPath":
				self.moviesPath=child.text
			elif child.tag == "seriesPath":
				self.seriesPath = child.text
			elif child.tag == "seriesMappingFile":
				self.seriesMappingFile = child.text
			elif child.tag == "deleteFolder":
				if child.text.lower() == "true":
					self.deleteFolder = True
				else :
					self.deleteFolder = False

		self.info("TorrentMover loaded.")




	def debug(self,message):
		logging.debug(message)

	def info(self,message):
		logging.info(message)

	def warn(self,message):
		logging.warn(message)

	def err(self,message):
		logging.error(message)


if __name__ == "__main__":
	logging.basicConfig(filename='/tmp/torrentmover.log',level=logging.DEBUG)

	if len(sys.argv) >= 2: 
		confFile=sys.argv[1]
	else:
		confFile  = "/etc/torrentmover.xml"

	fname=os.getenv('TR_TORRENT_NAME')
	fold=os.getenv('TR_TORRENT_DIR')
	if fname != None and fold != None:
		folder = "%s/%s" % (fold,fname)
		torrentMover = TorrentMover(confFile)
		torrentMover.unrarFinished(folder, fname)
		sys.exit(0)
	else:
		print "TR_TORRENT_NAME or TR_TORRENT_DIR not set!"
 		sys.exit(1)