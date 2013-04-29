#!/Users/jjk/Library/Enthought/Canopy_64bit/User/bin/python

import argparse
import urllib, ephem, datetime, tempfile, math
from astropy.io.votable import parse
from astropy.io.votable.tree import Field
import sys
import vos, os
import time

parser = argparse.ArgumentParser(description="Query the CADC for OSSOS observations.")
parser.add_argument('date', nargs='?', action='store',default='2013-01-01')
parser.add_argument('--runid', nargs='*', action='store', default= list(('13AP05','13AP06')))
parser.add_argument('--cal', action='store', default="RAW")
parser.add_argument('--outfile', action='store', default='vos:OSSOS/ObservingStatus/obsList')
parser.add_argument('--stack', action='store_true', default=False, 
    help="Make single status plot that stacks data accross multiple nights, instead of nightly sub-plots.")
opt = parser.parse_args()

runids = tuple(opt.runid)

try:
    mjd_yesterday = ephem.date(ephem.julian_date(ephem.date(opt.date))) - 2400000.5 
except Exception as e:
    sys.stderr.write("you said date = %s" %(opt.date))
    sys.stderr.write(str(e))
    sys.exit(-1)

## instead of having specific collumns in the SELECT clause below you could just put a '*' to get all possible columns.
## 
## the 'position_bounds' column provides a polygon that describes the edge of the field of the mosaic, not individual ccds.

data={"QUERY": """SELECT Observation.target_name as TargetName, COORD1(CENTROID(Plane.position_bounds)) AS RA, COORD2(CENTROID(Plane.position_bounds)) AS DEC, Plane.time_bounds_cval1 AS StartDate, Plane.time_exposure AS ExposureTime, Observation.instrument_name AS Instrument, Plane.energy_bandpassName AS Filter, Observation.collectionID AS dataset_name, Observation.proposal_id AS ProposalID, Observation.proposal_pi AS PI FROM caom.Observation AS Observation JOIN caom.Plane AS Plane ON Observation.obsID = Plane.obsID WHERE  ( Observation.collection = 'CFHT' ) AND Plane.time_bounds_cval1 > %d AND Plane.observable_ctype='%s' AND Observation.proposal_id IN %s """ %  ( mjd_yesterday, opt.cal, str(tuple(opt.runid)) ),
      "REQUEST": "doQuery",
      "LANG": "ADQL",
      "FORMAT": "votable"}

url="http://www.cadc.hia.nrc.gc.ca/tap/sync?"+urllib.urlencode(data)

# uncomment this to see the URL
#print data["QUERY"]
#print url

tmpFile = tempfile.NamedTemporaryFile()

urllib.urlretrieve(url,tmpFile.name)


vot = parse(tmpFile.name).get_first_table()
vot.array.sort(order='StartDate')
t=vot.array

stamp = "#\n# Last Updated: "+time.asctime()+"\n#\n"
header= "| %20s | %20s | %20s | %20s | %20s | %20s | %20s |\n"  % ( "EXPNUM", "OBS-DATE", "FIELD", "EXPTIME(s)", "RA", "DEC", "RUNID")
bar = "="*(len(header)-1)+"\n"

fout = vos.Client(certFile="/Users/jjk/.ssl/cadcproxy.pem").open(opt.outfile+".txt",mode=os.O_WRONLY)

t2 = None
fout.write(bar+stamp+bar+header)
# sys.stdout.write(bar+stamp+bar+header)
night_count = 0
for i in range(len(t)-1,-1,-1):
    row = t.data[i]
    sDate = str(ephem.date(row.StartDate + 2400000.5- ephem.julian_date(ephem.date(0))))[:20]
    t1 = time.strptime(sDate,"%Y/%m/%d %H:%M:%S")
    if t2 is None or math.fabs(time.mktime(t2)-time.mktime(t1)) > 3*3600.0:
        # sys.stdout.write(bar)
        night_count += 1
        fout.write(bar)
    t2 = t1
    ra = str(ephem.hours(math.radians(row.RA)))
    dec = str(ephem.degrees(math.radians(row.DEC)))
    line = "| %20s | %20s | %20s | %20.1f | %20s | %20s | %20s |\n" % ( str(row.dataset_name), str(ephem.date(row.StartDate + 2400000.5 - ephem.julian_date(ephem.date(0))))[:20], row.TargetName[:20], row.ExposureTime, ra[:20], dec[:20], row.ProposalID[:20] )
    fout.write(line)
    # sys.stdout.write(line)

fout.write(bar)
# sys.stdout.write(bar)
fout.close()
tmpFile.close()

## make a plot of the coverage

from matplotlib.pyplot import figure, show, savefig
from matplotlib.patches import Rectangle
from matplotlib import pyplot

width = 0.98
height  = 0.98

nrows = ( ( opt.stack and night_count ) or 1 ) 
fig = figure(figsize=(7,2*nrows))

t2 = None
count = 0
ra_min = t['RA'].max() + 1.5
ra_max = t['RA'].min() - 1.5
dec_min = t['DEC'].min() - 1.5
dec_max = t['DEC'].max() + 1.5

for row in reversed(t.data):
    sDate = str(ephem.date(row.StartDate + 2400000.5- ephem.julian_date(ephem.date(0))))[:20]
    t1 = time.strptime(sDate,"%Y/%m/%d %H:%M:%S")
    if t2 is None or ( math.fabs(time.mktime(t2)-time.mktime(t1)) > 3*3600.0 and opt.stack):
            count += 1
            ax = fig.add_subplot(nrows, 1, count, aspect='equal' )
            # ax.text(ra_max - 2.0, (dec_max + dec_min)/2.0, "%s/%s" % ( t1.tm_mon, t1.tm_mday), fontdict={'fontsize': 8} )
            ax.set_title("date from %s-%s-%s" % ( t1.tm_year, t1.tm_mon, t1.tm_mday), fontdict={'fontsize': 8} )
            ax.axis((ra_min,ra_max,dec_min,dec_max))
            ax.grid()
            ax.set_xlabel("RA (deg)", fontdict={'fontsize': 8} )
            ax.set_ylabel("DEC (deg)", fontdict={'fontsize': 8} )
    t2 = t1
    ra = row.RA - width/2.0
    dec = row.DEC - height/2.0
    ax.add_artist(Rectangle(xy=(ra,dec), height=height, width=width, edgecolor='b', lw=0.5, fill='g', alpha=0.33))


pyplot.title("CFHT coverage as of %s" % ( time.asctime() ))
tmpFile = tempfile.NamedTemporaryFile(suffix='.pdf')
savefig(tmpFile.name)
tmpFile.flush()
vos.Client(certFile="/Users/jjk/.ssl/cadcproxy.pem").copy(tmpFile.name,opt.outfile+".pdf")
tmpFile.close()