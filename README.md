PyloadMover
===========

Pyload Hook plugin, which moves downloaded files to movie or series folders.

Pyload tries to find a mapping series for the file first. If this is unsuccessful it will be handled as a movie.

Movies
-------------
For movies the plugin searches in the folder for .mkv or .avi files. It creates a folder named like the movie file and puts the file right there. 

Series
-------------
Series are a little more complex. Often Series are save on the disk in some folder hierachy like:

	Some.Series
		S.01
			Episode.01
			Episode.02
		S10
			Episode.01

PylaodMover tries to move the episode in the correct folder. For that a XML file (mover.xml) will be used to define some mappings. 

A basic file could look like this:

	<?xml version="1.0" encoding="UTF-8"?>
	<mappings>
		<series folder="Some.Series" name="The best series ever" renamePattern="some.series.S%sE%e.%f">
			<mapping>some.series</mapping>
			<mapping>myseries</mapping>
			<mapping season="10">series.x</mapping>
		</series>
	</mappings>

It adds a mapping for the series "The best series ever". The folder to place the series is called "Some.Series". 

Every Season will be placed in a seperated folder, which will be named S.XX (i.e. S.01 for season 1). If the folder does not exist, PyloadMover checks for a folder called SXX (i.e. S10 for season 10). If existing that will be used. If not, the folder will be created. Some file names do not contain the season number as digits, but as roman numerals. To map these correct to the right season, the attribute season could be specified. In the example this is done for season 10.

The episodes will be moved to the season folder of the series. If a renamePattern is defined the file is renamed to that pattern. That could be used to make sure every episode is named the same way. There are some placeholders, which will be replaced:

*	%s will be replaced by the season number (two digits)
*	%e will be replaced by the episode number (also two digits)
*	%f will be replaced by the file ending (mkv or avi)

In the above example we use "`some.series.S%sE%e.%f`". So the 12 episode of the 7 season will be called "`some.series.S07E12.mkv`"


Settings
-------------
### Activated (bool)
Defines if the plugin is active or not.
Default: False

### movieSize (int)
Defines the size a file in MB must have to be treated as a movie.
If set to -1 every file will be handled as a series first and if no mapping is found be treated as a movie.
Default: -1

### moviesPath (str)
Defines the base folder where all movies will be put.
Default: /share/Multimedia/Movies

### seriesPath (str)
Defines the base folder where all series will be put.
Default: /share/Multimedia/Series

### seriesMappingFile (str)
Defines the file name for the mapping XML file. The default folder for this file is the pyload data folder. Also an absolute path could be used.
Default: mover.xml

### deleteFolder (bool)
Defines if the download folder will be deleted after processing. The folder will only be deleted if the file could be moved.
Default: True




Things to come
-------------
It would be nice, if IMDB and so would be search for infos to the movie or episode and automatically write this info to .nfo files for XBMC.
