import os
import shutil
import xml.etree.ElementTree as ET
import re
import traceback


class Mover():
    """
    Moves files to movie or series folder.
    """
    __name__ = "Mover"
    __version__ = "0.1"
    __description__ = "Moves finished downloads to movies or series folders."

    __author_name__ = ("r00tat")
    __author_mail__ = ("pyload@frig.at")

    activated = False
    movieSize = 0
    moviesPath = None
    seriesPath = None
    seriesMappingFile = None
    deleteFolder = True

    videoFileEndings = ["mkv", "avi", "mp4", "mov", "mpg", "mpeg"]

    """
    load all config vars
    """
    def loadConfig(self):
        pass

    """
    initialize plugin
    """
    def initialize(self):
        self.loadConfig()
        self.initSeriesMapping()
        self.log_debug("Initialized.")

    """
    hook for finished unrar
    """
    def unrarFinished(self, folder, fname):
        self.log_info("finished unrar of %s in %s" % (fname, folder))

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
                            fullname = os.path.join(dirpath, filename)
                            self.log_info("found video %s %d" % (fullname, os.path.getsize(fullname)))
                            found = True

                            try:

                                if self.movieSize > 0:
                                    if os.path.getsize(fullname) / (1024 * 1024) >= self.movieSize:
                                        # Movie
                                        self.log_info("found movie")
                                        self.handleMovie(folder, dirpath, filename)
                                    else:
                                        # Series
                                        self.log_info("found series")
                                        self.handleSeries(folder, dirpath, filename)

                                else:
                                    # try as series first, otherwise treat as movie
                                    if not self.handleSeries(folder, dirpath, filename):
                                        self.log_info("no series, try as movie")
                                        self.handleMovie(folder, dirpath, filename)

                            except Exception, e:
                                self.log_err("failed to move or series file %s into folder: %s" % (fullname, e))
                                self.log_err("Traceback %s" % traceback.format_exc(e))
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
    def handleSeries(self, folder, dirpath, filename):

        filenameLower = filename.lower()
        # fullname = os.path.join(dirpath, filename)
        # fileEnding = self.getFileEnding(filename)

        #search for mapping
        tree = ET.parse(self.seriesMappingFile)
        root = tree.getroot()

        # go through all series nodes
        for series in root.getiterator("series"):

            if series.find("mapping") is None:
                if series.get("name").lower() in filenameLower:
                    self.log_info("name found %s in %s" % (series.get("name"), filename))
                    return self.renameEpisode(folder, dirpath, filename, series)

            # check mapping
            for mapping in series.getiterator("mapping"):
                if mapping.text.lower() in filenameLower:
                    self.log_info("mapping found %s for %s" % (mapping.text, series.get("name")))

                    # move element to series
                    return self.renameEpisode(folder, dirpath, filename, series, mapping)

                    break

        self.log_info("did not find a mapping for series")
        return False

    """
    a mapping has been found, so move the episode in the correct folder
    """
    def renameEpisode(self, folder, dirpath, filename, series, mapping=None):

        # filenameLower = filename.lower()
        fullname = os.path.join(dirpath, filename)
        fileEnding = self.getFileEnding(filename)

        seriesFolderName = series.get("folder")
        if seriesFolderName is None:
            seriesFolderName = series.get("name")
            if seriesFolderName is None:
                #again?
                self.log_warn("did not find a folder or name in series element")
                return False
            seriesFolderName = seriesFolderName.replace(' ', ".")

        seriesFolder = os.path.join(self.seriesPath, seriesFolderName)

        seasonNum = None
        episodeNum = None

        if re.match('.*S\.?(\d+)\.?E\.?(\d+).*', filename, flags=re.IGNORECASE):
            m = re.search('.*S\.?(\d+)\.?E\.?(\d+).*', filename, flags=re.IGNORECASE)
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

        if mapping is not None and mapping.get("season"):
            # overide season mapping
            seasonNum = mapping.get("season")

        if len(seasonNum) == 1:
            seasonNum = "0%s" % (seasonNum)

        if len(episodeNum) == 1:
            episodeNum = "0%s" % (episodeNum)

        self.log_info("Season: %s Episode: %s" % (seasonNum, episodeNum))

        seasonFolder = os.path.join(seriesFolder, "S.%s" % (seasonNum))

        if not os.path.isdir(seasonFolder):
            if os.path.isdir(os.path.join(seriesFolder, "S%s" % (seasonNum))):
                seasonFolder = os.path.join(seriesFolder, "S%s" % (seasonNum))
            else:
                # create folder
                os.makedirs(seasonFolder)

        self.log_info("Season folder: %s" % (seasonFolder))

        destFilename = filename

        # optional: rename files
        if series.get("renamePattern") is not None:
            destFilename = series.get("renamePattern").replace("%s", seasonNum).replace("%e", episodeNum).replace("%f", fileEnding)

        finalPath = os.path.join(seasonFolder, destFilename)
        self.log_info("moving %s to %s" % (fullname, finalPath))
        shutil.move(fullname, finalPath)

        if self.deleteFolder:
            self.log_info("removing folder %s" % (folder))
            shutil.rmtree(folder)

        return True

    def handleMovie(self, folder, dirpath, filename):
        # filenameLower = filename.lower()
        fullname = os.path.join(dirpath, filename)
        fileEnding = self.getFileEnding(filename)

        # create foldername out of filename (without file ending)
        folderName = os.path.join(self.moviesPath, filename.replace(".%s" % (fileEnding), ""))

        self.log_info("moving to %s " % (folderName))
        # create dirs
        os.makedirs(folderName)

        shutil.move(fullname, folderName)

        # delete downloaded folder if necesary
        if self.deleteFolder:
            self.log_info("removing folder %s " % (folder))
            shutil.rmtree(folder)

        return True

    """
    get the file ending of a filename
    """
    def getFileEnding(self, filename):
        lastDot = filename.rfind(".")

        if lastDot == -1 or lastDot+1 == len(filename):
            # no file ending or dot at the end
            return None

        fileEnding = filename[lastDot+1:].lower()

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
            series.set("name", "Some series title")
            series.set("folder", "My.Series.Folder")

            # create mappings
            mapping = ET.SubElement(series, "mapping")
            mapping.text = "someseries"

            mapping = ET.SubElement(series, "mapping")
            mapping.text = "some.series"

            mapping = ET.SubElement(series, "mapping")
            mapping.text = "my.series"

            tree = ET.ElementTree(root)
            tree.write(self.seriesMappingFile, "utf-8")

        else:
            try:
                tree = ET.parse(self.seriesMappingFile)
                root = tree.getroot()
                pass
            except Exception, e:
                # file is wrong
                self.log_err("could not load mapping file %s: %s" % (self.seriesMappingFile, e))
            else:
                pass
            finally:
                pass

    def log_debug(self, message):
        pass

    def log_info(self, message):
        pass

    def log_warn(self, message):
        pass

    def log_err(self, message):
        pass
