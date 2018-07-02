import sys, time, headless_usrp, headless_usrp_freqshift, headless_usrp_giantpulse, os, datetime, headless_usrp_freqshift_giantpulse
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from bandPassPlotter import bandPassPlotter
from singlePulsePlotter import singlePulsePlotter

separationLimit = 20#in degrees
waitTime = 10#in seconds
integrationTime = 280 # seconds
target = SkyCoord(ra="05h43m32s", dec="22d00m52s", frame='icrs')


#---------You shouldn't have to adjust anything below this line---------#
whiteHall = EarthLocation(lat=39.632858*u.deg, lon=-79.954926*u.deg, height=280*u.meter)
t = Time(datetime.datetime.utcnow())
#https://mail.scipy.org/pipermail/astropy/2015-March/003645.html
pointing = SkyCoord(az=180*u.degree, alt=72*u.degree, frame='altaz', location=whiteHall, obstime=t) 
pointingRADEC =  pointing.transform_to('icrs')

separationNow = target.separation(pointingRADEC).degree
print("Telescope Object Separation = {0:.2f} deg".format(separationNow))

os.chdir("/home/odroid/gnuradio/lib/uhd/utils/share/uhd/images")#need to be in this directory for the ettus board to run

if separationNow < separationLimit:
    tb1 = headless_usrp_giantpulse.headless_usrp_giantpulse()#this is copied from gnuradio's main()
    tb1.start()
    time.sleep(integrationTime)
    tb1.stop()
    tb1.wait()
    singlePulsePlotter(tb1.giantout, tb1.display_integration).plot()
else:
    tb1 = headless_usrp.headless_usrp() #take data, its writen this why to get the
    tb1.start()
    time.sleep(integrationTime)
    tb1.stop()
    tb1.wait()

time.sleep(waitTime)

if separationNow < separationLimit:
    tb2 = headless_usrp_freqshift_giantpulse.headless_usrp_freqshift_giantpulse()
    tb2.start()
    time.sleep(integrationTime)
    tb2.stop()
    tb2.wait()
    singlePulsePlotter(tb2.giantout, tb2.display_integration).plot()
else:
    tb2 = headless_usrp_freqshift.headless_usrp_freqshift()#take data
    tb2.start()
    time.sleep(integrationTime)
    tb2.stop()
    tb2.wait()

bandPassPlotter(tb1.recfile, tb2.recfile, tb1.vec_length, tb1.freq, tb2.freq).plot()

