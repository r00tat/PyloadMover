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


#### Mover.xml
PyloadMover tries to move the episode in the correct folder. For that a XML file (mover.xml) will be used to define some mappings. 

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

#### Mappings

PyloadMover searches the mover.xml for series elements. Each series XML element represents one series.   
This series element contains one mandatory attribute `name` and some other optional. In our example the series is called "`The best series ever`". 

The `folder` attribute is optional and could be used to explicitly specify the folder name. If no folder attribute given, the folder will be the name, with spaces "` `" replaced by "`.`"

If a `renamePattern` is given, the file will be renamed after moving it to the correct folder. See [Renameing](#renameing) for more details.

Each series can contain multiple mappings. Each `mapping` XML elements text will be searched in the filename. If the filename contains this text, it will be considered a match and will be moved to the series folder. The search is case insensitive.

#### Season folders

Every Season will be placed in a seperated folder, which will be named `S.XX` (i.e. `S.01` for season 1). If the folder does not exist, PyloadMover checks for a folder called `SXX` (i.e. `S10` for season 10). If existing that will be used. If not, the folder will be created. Some file names do not contain the season number as digits, but as roman numerals. To map these correct to the right season, the attribute season could be specified. In the example this is done for season 10.


#### Renameing

The episodes will be moved to the season folder of the series. If a renamePattern is defined the file is renamed to that pattern. That could be used to make sure every episode is named the same way. There are some placeholders, which will be replaced:

*	%s will be replaced by the season number (two digits)
*	%e will be replaced by the episode number (also two digits)
*	%f will be replaced by the file ending (mkv or avi)

In the above example we use "`some.series.S%sE%e.%f`". So the 12 episode of the 7 season will be called "`some.series.S07E12.mkv`"

#### Season and Episode numbers

The Season and Episode will be extraced from the file name. All patterns are case insensitive. The following patterns are tried.


1.	`S\.?(\d+)\.?E\.?(\d+)` filename contains S and E before season and episode number  
	this is the best possible match and will match the following)	*	`S01E02` => season 1, episode 2
	*	`S01.E02` => season 1, episode 2
	*	`s01.e02` => season 1, episode 2
	*	`S.01E.02` => season 1, episode 2
	*	`S.01.E.02` => season 1, episode 2
	*	`S1E2` => season 1, episode 2
	*	`S1E12` => season 1, episode 12
	*	`S01E2` => season 1, episode 2

2.	`(\d+)(\d\d)` at least 3 digits in a row  
	the last 2 digits are used for the episode, all others for the season
	*	`103` => season 1, episode 3
	*	`0406` => season 4, episode 6
	*	`1205` => season 12, episdode 5
	*	`1024` => season 10, episode 24
	
3.	`(\d\d)` only two digits will always be season 1 and the episode
	*	`01` => season 1, episode 1
	*	`12` => season 1, episode 12
4.	`(\d+)` one or more digits will always be season 1 and the episode
	*	`1` => season 1, episode 1
	*	`5` => season 1, episode 5
	*	`123` => season 1, episode 123
5.	all other files will be season 1, episode 1


With this rules these filenames would equal the following season and episode

*	`my-series.S04.E03.avi` => season 4, episode 3
*	`my-series.s02E07.avi` => season 2, episode 7
*	`my-series.S04E03.This.is.not.the.End.mkv` => season 4, episode 3
*	`my-series.S0403.avi` => season 4, episode 3
*	`my-series.0403.avi` => season 4, episode 3
*	`my-series.1207.avi` => season 12, episode 7
*	`my-series.403.avi` => season 4, episode 3
*	`my-series.03.avi` => season 1, episode 3
*	`my-series.123.avi` => season 1, episode 123

The season could also be overwritten by [mappings](#mappings).



Settings
-------------

#### Activated (bool)
Defines if the plugin is active or not.  
Default: `False`

#### movieSize (int)
Defines the size a file in MB must have to be treated as a movie.  
If set to -1 every file will be handled as a series first and if no mapping is found be treated as a movie.  
Default: `-1`

#### moviesPath (str)
Defines the base folder where all movies will be put.  
Default: `/share/Multimedia/Movies`

#### seriesPath (str)
Defines the base folder where all series will be put.  
Default: `/share/Multimedia/Series`

#### seriesMappingFile (str)
Defines the file name for the mapping XML file. The default folder for this file is the pyload data folder. Also an absolute path could be used. See also [the example mover.xml file](#moverxml).  
Default: `mover.xml`

#### deleteFolder (bool)
Defines if the download folder will be deleted after processing. The folder will only be deleted if the file could be moved.  
Default: `True`




Things to come
-------------
It would be nice, if IMDB and so would be search for infos to the movie or episode and automatically write this info to .nfo files for XBMC.
