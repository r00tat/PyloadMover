from module.plugins.Hook import Hook
from .Mover import Mover
import traceback


class PyloadMover(Hook, Mover):
    """
    Moves files to movie or series folder.
    """
    __name__ = "PyloadMover"
    __version__ = "0.21"
    __description__ = "Moves finished downloads to movies or series folders."
    __config__ = [("activated", "bool", "Activated", "False"),
                  ("movieSize", "int", "Treat files larger than this MB as movie", "-1"),
                  ("moviesPath", "str", "Folder for movies", "/share/Multimedia/Movies"),
                  ("seriesPath", "str", "Folder for series", "/share/Multimedia/Series"),
                  ("seriesMappingFile", "str", "XML File for mapping file names to series", "mover.xml"),
                  ("deleteFolder", "bool", "Delete dowload folder after renaming", "True")]
    #__threaded__ = ["downloadFinished"]
    __author_name__ = ("r00tat")
    __author_mail__ = ("pyload@frig.at")

    event_map = {"coreReady": "initialize",
                 "unrarFinished": "unrarFinished",
                 "pluginConfigChanged": "pluginConfigChanged",
                 "archive_extracted": "archive_extracted"}

    """
    initialize plugin
    """
    def initialize(self):
        self.loadConfig()
        self.initSeriesMapping()
        self.log_debug("Initialized.")

    """
        extracted Hook
    """
    def archive_extracted(self, pyfile, folder, filename, files, *args, **kwargs):
        try:
            self.log_info("test?")
            self.log_info("folder: %s" % folder)
            self.log_info("filename %s" % filename)
            # self.log_info("files: %s" % files)
            self.log_info("filename %s" % filename)

            self.unrarFinished(folder, filename)
        except Exception, e:
            print "Error %s", e
            print traceback.format_exc()

    """
    load all config vars
    """
    def loadConfig(self):
        self.activated = self.getConfig("activated")
        self.movieSize = self.getConfig("movieSize")
        self.moviesPath = self.getConfig("moviesPath")
        self.seriesPath = self.getConfig("seriesPath")
        self.seriesMappingFile = self.getConfig("seriesMappingFile")
        self.deleteFolder = self.getConfig("deleteFolder")
        self.initSeriesMapping()
        self.log_info("PyloadMover loaded.")

    """
    hook for plugin Config changed
    """
    def pluginConfigChanged(self, moduleName, param, value):
        if moduleName == "PyloadMover":
            self.log_info("Plugin config changed: %s=%s" % (param, value))
            if param == "activated":
                self.activated = value
            elif param == "movieSize":
                self.movieSize = value
            elif param == "moviePath":
                self.moviesPath = value
            elif param == "seriesPath":
                self.seriesPath = value
            elif param == "seriesMappingFile":
                self.seriesMappingFile = value
                self.initSeriesMapping()
            elif param == "deleteFolder":
                self.deleteFolder = value

        #self.loadConfig()
    def log_debug(self, message):
        self.logDebug(message)

    def log_info(self, message):
        self.logInfo(message)

    def log_warn(self, message):
        self.logWarn(message)

    def log_err(self, message):
        self.logError(message)
