import sys, time, headless_usrp, headless_usrp_freqshift, headless_usrp_giantpulse, os, datetime, headless_usrp_freqshift_giantpulse
#import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from subprocess import call

whiteHall = EarthLocation(lat=39.632858*u.deg, lon=-79.954926*u.deg, height=280*u.meter)

t = Time(datetime.datetime.utcnow())
#https://mail.scipy.org/pipermail/astropy/2015-March/003645.html
pointing = SkyCoord(az=180*u.degree, alt=72*u.degree, frame='altaz', location=whiteHall, obstime=t) 

pointingRADEC =  pointing.transform_to('icrs')

target = SkyCoord(ra="05h43m32s", dec="22d00m52s", frame='icrs')
sep = target.separation(pointingRADEC).degree
print sep

os.chdir("/home/odroid/gnuradio/lib/uhd/utils/share/uhd/images")#need to be in this directory for the ettus board to run

#if sep<10.0:
#    headless_usrp_giantpulse.main()
#else:
#    headless_usrp.main() #take data
headless_usrp_giantpulse.main()
#time.sleep(30)
#if sep<10.0:
#    headless_usrp_freqshift_giantpulse.main()
#else:
#    headless_usrp_freqshift.main()#take data

#time.sleep(1)

#call(['/bin/bash','/home/dspradio/grc_data/plotter.sh'])
