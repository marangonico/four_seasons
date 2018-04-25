# Four Seasons

### Intro
Wouldn't be nice to load your sim and find the scenery representing a plausible season,
based on location and period of the year?

What about having an october with colored leafes and naked trees in winter?

Well actually this could be already accomplished using existing freeware libraries, but..
* what about having a snow coverage depending on season and distance from the poles?
* what about having ground snow only if within certain temperature ranges or with ongoing precipitations?

### Description
Four Seasons is a freeware plugin which scope is driving the changing of seasons from a scenery point of view.

The plugin is half of what you need, the second half are compatible sceneries.

Since this plugin is based on existing freeware sceneries, you have to modify these sceneries in order to make them
compatible.

This isn't a plug & play software, you should spend some of your time reading and trying (exploring I'd prefer to say).
Please do not expect full support for installing the plugin and the related libraries.
Other than programming this software and releasing it for free, I'd prefer to spend my time with my family and
cultivating my hobbies. I hope you understand it. ;-)

**Note: _Don't be scared, these modifications usually consist in changing 1 or 2 lines of text in a file
called library.txt_**


### How it works?
###### Under the hood:
- It estimates the season appearence and exposes a single dataref with a value representing the season.
- If a scenery is binded (through a REGION_DREF directive) to this dataref it will react accordingly (the plugin will force a scenery reload to make it happens).
###### In few words:
- You set a place and/or a date for you aircraft and it tells the sceneries to reload with the correct set of textures

#### Requirements:
- Python 2.7.x (https://www.python.org/downloads/)
- Pyhton Interface Plugin by Sandy Barbour (http://www.xpluginsdk.org/python_interface.htm)
- Seasons Library by einstein (https://forums.x-plane.org/index.php?/files/file/29015-seasons-dataref-driven-libraries/)
- Seasons Spring by madmaxland (https://forums.x-plane.org/index.php?/files/file/35641-seasons-spring-v10/&page=2&tab=comments#comment-213081)
- Seasonal Fall Ground Textures by madmaxland (https://forums.x-plane.org/index.php?/files/file/35658-seasonal-fall-ground-textures/)
- Seasonal Winter Ground Textures by madmaxland (https://forums.x-plane.org/index.php?/files/file/35680-seasonal-winter-ground-textures/)

## Sceneries
Table of Contents:
- Instructions for using the seasons sceneries under XP11 (without the plugin)
- Making the sceneries compatible with Four Seasons

### Instructions for using the seasons sceneries under XP11
**Taken and adapted with permission of crisk73 from [this post](https://forums.x-plane.org/index.php?/forums/topic/90168-seasons-dataref-driven-libraries-support-and-discussion/&do=findComment&comment=1258385).**

1. If your sceneries are already working with XP11 or you are using
XP10, you can skip this step.

2. Since we don't need all the folders inside the original seasons
packages, you could read this section and apply the changes only to the
relevant directories (You'll find which in the next section)

The original post is referred to the "_Seasons Library by einstein_",
here I'm also including "_Seasons Spring by madmaxland_"

**A few notes:**

**1. Making a backup of all these files is always a good rule.**

**2. You won't need all the folders inside the seasons packages,
but here we explain how to change them all**

**3. Summer is never mentioned because summer textures are the default
ones.**

If you have uncompressed all the sceneries packages, these are the
folders you should end with:
- Seasonal Fall N
- Seasonal Snow N
- Seasonal Snow ND
- Seasons_assets
- Seasons_N_Autumn
- Seasons_N_Spring
- Seasons_N_Winter1
- Seasons_N_Winter2
- Seasons_Runways
- Seasons_S_Autumn
- Seasons_S_Winter


###### Copy the following folders

###### 1) From Seasons_assets copy the following folders:
- Autumn
- Autumn_opensceneryx
- Autumn_R2
- Autumn_w2xp
###### into:
- Seasons_N_Autumn
- Seasons_S_Autumn

###### 2) From Seasons_assets copy the following folders:
- Winter_NS_R2
- Winter_w2xp
- WinterNS
- WinterNS_opensceneryx
###### into:
- Seasons_N_Winter1
- Seasons_N_Winter2
- Seasons_S_Winter

###### 3) From Seasons_assets copy the following folders:
- SpringNS_opensceneryx
- SpringNS
- Spring_w2xp
- Spring_NS_R2
###### into:
- Seasons_N_Spring

###### 4) In each folder open the file *library.txt* with a text editor (notepad is ok but I'd suggest notepad++) and substitute the following strings:
- "*../Seasons_assets/*" (without commas)
- "*../Season _assets/*" (different from the previous one since it has a tab before the character "*_*")

###### with the null string blank (-->> that is remove all the occurrences), then save on exit.

###### 5) Delete the folder *Seasons_assets*

**Example:**

The block
```
######	Winter NS forests
EXPORT	lib/g8/broad_cld_dry.for	../Seasons_assets/WinterNS/Win_NS_broad_cld_dry.for
EXPORT	lib/g8/broad_cld_rain.for	../Seasons_assets/WinterNS/Win_NS_broad_cld_rain.for
EXPORT	lib/g8/broad_cld_sdry.for	../Seasons_assets/WinterNS/Win_NS_broad_cld_sdry.for
```
Should become
```
######	Winter NS forests
EXPORT	lib/g8/broad_cld_dry.for	WinterNS/Win_NS_broad_cld_dry.for
EXPORT	lib/g8/broad_cld_rain.for	WinterNS/Win_NS_broad_cld_rain.for
EXPORT	lib/g8/broad_cld_sdry.for	WinterNS/Win_NS_broad_cld_sdry.for
```

### Making the sceneries compatible with Four Seasons
First we have to choose only 1 folder per season winter.
If you are starting with the following directories:
- Seasonal Fall N
- Seasonal Snow N
- Seasonal Snow ND
- Seasons_N_Autumn
- Seasons_N_Spring
- Seasons_N_Winter1
- Seasons_N_Winter2
- Seasons_S_Autumn
- Seasons_S_Winter

After all this work You should end up with these:
- Seasonal Fall
- Seasonal Snow
- Seasons_Autumn
- Seasons_Spring
- Seasons_Winter

So..
1. Make a backup if needed
2. Rename "_Seasonal Fall N_" in "_Seasonal Fall_"
3. Rename "_Seasonal Snow N_" in "_Seasonal Snow_"
4. Rename "_Seasons_N_Autumn_" in "_Seasons_Autumn_"
5. Rename "_Seasons_N_Spring_" in "_Seasons_Spring_"
6. Rename "_Seasons_N_Winter1_" in "_Seasons_Winter_"
7. Delete or move the others.

Now, in order to make these sceneries working with Four Seasons we have
to modify again the file _library.txt_.

Inside each library.txt you'll find (in the first part or header of the
file) two directives:
```
REGION_BITMAP
REGION_DREF
```
We have to comment these directives putting a "_#_" as the first
character of each line.
Then we have to insert 2 other directives:
```
REGION_ALL
REGION_DREF (followed by the correct dataref)
```
Here I have to explain how Four Seasons injects (more or less) the
season into these sceneries.

Four Season exposes a custom dataref called "_nm/four_seasons/season_".

This dataref can assume the following values:
- **10** (Season=Spring)
- **20** (Season=Summer)
- **30** (Season=Fall)
- **40** (Season=Winter without ground snow)
- **45** (Season=Winter with ground snow)
- **50** (Season=Deep Winter) (Only working with Terramax compatible sceneries)

Let's say we want to adapt the "Season Spring" package.
All we have to do is:
- Open the file "_Seasons_Spring\library.txt_"
- Comment REGION_BITMAP
- Add the REGION_ALL as described here above.
- Insert the following REGION_DREF:
```
REGION_DREF nm/four_seasons/season == 10
```
That's to say, "_Activate this scenery if the season dataref is equal
to 'Spring'_"

This is an excerpt of the header after these changes:
```
A
800
LIBRARY

#####     Seasonal forests and trees
#####     By Richard Elliott
#####     Version 1.3     12 November 2015

###############################
#####     Northern Hemisphere     #####
#####	        Spring	    #####
###############################

REGION_DEFINE Nhem_spring

#####     Seasonal region defined by white area of 360x180 bitmap.	Each pixel represents 1x1 degree lat/long

#REGION_BITMAP Nhem.png
REGION_ALL

#####     Spring in days starting from Jan 1st.

#REGION_DREF sim/time/local_date_days >= 91
#REGION_DREF sim/time/local_date_days <= 127
REGION_DREF nm/four_seasons/season == 10

#####    Assign regional art assets
[...]
```
Proceed in the same way with
###### Fall:
File to be modified:
- Seasons_Autumn\library.txt
- Seasonal_Fall\library.txt
```
REGION_DREF nm/four_seasons/season == 30
```
###### Winter without ground snow:
File to be modified:
- Seasons_Winter\library.txt
```
REGION_DREF nm/four_seasons/season == 40
```
###### Winter with ground snow:
File to be modified:
- Seasonal_Snow\library.txt
```
REGION_DREF nm/four_seasons/season >= 45
```
**Note that here I've wrote "_equal or grather than 45_", so this
scenery will be activated also with "_winter deep_".**
## Usage:
At startup Four Season will calculate the season it considers accurate
and feeds the datarefs accordingly.

After each aircraft repositioning or date change, it recalculates the
season.

**Note: Season changes will start and automatic reload of the scenery.**

### The control panel
The control panel window shows the following elements:
- **Determine season automatically:** in this mode Four Seasons tries to
caluculate an appropriate representation of the season
- **Manual selections:** select one of the listed seasons and press
"Save&Apply", Four Season will maintain your choice.
- **Feed terramax datarefs:** Four Season will feed the datarefs used by
Terramax compatible sceneries
- **Force Refresh:** Four Season will start a reload of the scenery and
textures
- **Refresh Season:** Four Season will recalculate the season and start
a reload of the scenery and textures if necessary
- **Save&Apply:** Four Season will save current settings and apply them.
A reload of the scenery and textures could be started.


#### Terramax:
I do not own Terramax, but I've seen how it works and you can download
UrbanMAXX (http://maxx-xp.com/urbanmaxx-v3-tm) for free and use it with
Four Seasons, just enable the terramax option.


#### FAQ:
- **Q**: What's the difference between Seasons and Seasonal packages?
- **A**: Seasons changes objects while Seasonal acts on ground textures