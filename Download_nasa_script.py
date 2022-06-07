# EXTRA information
"""
before staring need to create a .netrc file
"
> touch .netrc

> echo "machine urs.earthdata.nasa.gov login USERNAME password PASSWORD " > .netrc

> chmod 0600 .netrc

"
https://earthdata.readthedocs.io/en/latest/
"""

from earthdata import Auth, DataGranules, DataCollections, Store
import os

auth = Auth().login(strategy="netrc") # if we want to access NASA DATA in the cloud

# Search details

SHORTNAME="MCD43A2"
COLLECTION='061'
YEAR='2021'
STMONTH='07'
ENDMONTH='09'
STARTDATE=YEAR+'-'+STMONTH+'-01'
ENDDATE=YEAR+'-'+ENDMONTH+'-01'
MINLON=-180
MINLAT=70
MAXLON=180
MAXLAT=90
CLOUDMIN=0
CLOUDMAX=10
localdir=os.path.join(os.getcwd(),SHORTNAME,COLLECTION,YEAR)


# Create the Query

granules=DataGranules().short_name(SHORTNAME).version(COLLECTION)
granules=granules.temporal(STARTDATE, ENDDATE).bounding_box(MINLON,MINLAT,MAXLON,MAXLAT)
print(granules.hits())
GranuleQuery=granules.cloud_cover(min_cover=CLOUDMIN,max_cover=CLOUDMAX)
print(GranuleQuery.hits())

GQ = GranuleQuery.get()

# Download the files

files = Store(auth).get(GQ, local_path=localdir)
