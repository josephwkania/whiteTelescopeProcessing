import sys, time, os, datetime
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from bandPassPlotter import bandPassPlotter
from subprocess import Popen, PIPE

separationLimit = 10#in degrees
waitTime = 10#in seconds
integrationTime = 280 # seconds
fast_integrationPulse = 0.0005#when tapping the fast_integration output, in seconds
fast_integrationNoPulse = 0.5 #when fast integration is not tapped [ie not used], in seconds 
freqOne = 1.4205e9
freqTwo = 1.4202e9
sampleRate = 2.5e6
vecLength = 1024
source = "crab"
prefixOne = "/home/dspradio/grc_data/"
prefixTwo = "/home/dspradio/freq_shifts/"
prefixGiant = "/home/dspradio/giantPulses/"

t = Time(datetime.datetime.utcnow())
whiteHall = EarthLocation(lat=39.632858*u.deg, lon=-79.954926*u.deg, height=280*u.meter)
#https://mail.scipy.org/pipermail/astropy/2015-March/003645.html
pointing = SkyCoord(az=180*u.degree, alt=72*u.degree, frame='altaz', location=whiteHall, obstime=t)
target = SkyCoord(ra="05h43m32s", dec="22d00m52s", frame='icrs')

#---------You shouldn't have to adjust anything below this line---------#
pointingRADEC =  pointing.transform_to('icrs')
DECJ= pointingRADEC.dec.dms[0]*10000 + pointingRADEC.dec.dms[1]*100 + pointingRADEC.dec.dms[2]
RAJ= pointingRADEC.ra.hms[0]*10000 + pointingRADEC.ra.hms[1]*100 + pointingRADEC.ra.dms[2]
separationNow = target.separation(pointingRADEC).degree
print("Telescope Object Separation = {0:.2f} deg".format(separationNow))
print("Telescope Dec={0:.2f}".format(DECJ))
print("Telescope RAJ={0:.2f}".format(RAJ))

os.chdir("/home/odroid/gnuradio/lib/uhd/utils/share/uhd/images")#need to be in this directory for the ettus board to run

if True: #separationNow < separationLimit:
    import headless_usrp_giantpulse
    #from singlePulsePlotter import singlePulsePlotter
    tb1 = headless_usrp_giantpulse.headless_usrp_giantpulse(fast_integration=fast_integrationPulse, prefix=prefixOne, samp_rate=sampleRate, vec_length=vecLength, freq=freqOne, giant_prefix=prefixGiant)#this is copied from gnuradio's main()
    tb1.start()
    time.sleep(integrationTime)
    tb1.stop()
    tb1.wait()
    import filterbank as fb
    spdic = {}
    spdic["telescope_id"] = int(0)
    spdic["macnine_id"] = int(0)
    spdic["source_name"] = str(source)
    spdic["barycentric"] = int(0)
    spdic["src_raj"] = float(RAJ)
    spdic["src_dej"] = float(DECJ)
    spdic["nbits"] = int(32)
    spdic["nchans"] = int(vecLength)
    spdic["nifs"] = int(1)
    spdic["fch1"] = float((freqOne-sampleRate/2.0+sampleRate/vecLength)/10.0**6.0)
    spdic["foff"] = float(sampleRate/(vecLength*10.0**6.0))
    spdic["tsamp"] = float(fast_integrationPulse)
    spdic["tstart"] = float(t.mjd)
    
    filterbank = fb.create_filterbank_file(tb1.giantout_bin.split('.bin')[0]+".head", header=spdic, nbits=32)
    filterbank.close()
    command = '/bin/cat ' +  tb1.giantout_bin.split('.bin')[0] + ".head " +  tb1.giantout_bin + ' > ' +  tb1.giantout_bin.split('.bin')[0]+".fil"
    fbmaker = Popen(command, stdout=PIPE, shell=True)
    output=fbmaker.communicate()[0]
    fbmaker.wait()
    remover = Popen('rm '+  tb1.giantout_bin.split('.bin')[0] + ".head " +  tb1.giantout_bin, stdout=PIPE, shell=True)
    output=remover.communicate()[0]
    
    #singlePulsePlotter(tb1.giantout, fast_integrationPulse).plot()
else:
    import headless_usrp
    tb1 = headless_usrp.headless_usrp(fast_integration=fast_integrationNoPulse, prefix=prefixOne, samp_rate=sampleRate, vec_length=vecLength, freq=freqOne)
    tb1.start()
    time.sleep(integrationTime)
    tb1.stop()
    tb1.wait()

time.sleep(waitTime)

if True:#separationNow < separationLimit:
    tb2 =  headless_usrp_giantpulse.headless_usrp_giantpulse(fast_integration=fast_integrationPulse, prefix=prefixTwo, samp_rate=sampleRate, vec_length=vecLength, freq=freqTwo, giant_prefix=prefixGiant)
    tb2.start()
    time.sleep(integrationTime)
    tb2.stop()
    tb2.wait()
    
    spdic = {}
    spdic["telescope_id"] = int(0)
    spdic["macnine_id"] = int(0)
    spdic["source_name"] = str(source)
    spdic["barycentric"] = int(0)
    spdic["src_raj"] = float(RAJ)
    spdic["src_dej"] = float(DECJ)
    spdic["nbits"] = int(32)
    spdic["nchans"] = int(vecLength)
    spdic["nifs"] = int(1)
    spdic["fch1"] = float((freqOne-sampleRate/2.0+sampleRate/vecLength)/10.0**6.0)
    spdic["foff"] = float(sampleRate/10.0**6.0)
    spdic["tsamp"] = float(fast_integrationPulse)
    spdic["tstart"] = float(t.mjd)
    
    filterbank2 = fb.create_filterbank_file(tb2.giantout_bin.split('.bin')[0]+".head", header=spdic, nbits=32)
    filterbank2.close()
    command2 = '/bin/cat ' +  tb2.giantout_bin.split('.bin')[0] + ".head " +  tb2.giantout_bin + ' > ' +  tb2.giantout_bin.split('.bin')[0]+".fil"
    fbmaker2 = Popen(command2, stdout=PIPE, shell=True)
    output2=fbmaker2.communicate()[0]
    fbmaker2.wait()
    remover2 = Popen('rm '+  tb2.giantout_bin.split('.bin')[0] + ".head " +  tb2.giantout_bin, stdout=PIPE, shell=True)
    output2=remover2.communicate()[0]
    #singlePulsePlotter(tb2.giantout, fast_integrationPulse).plot()
else:
    tb2 = headless_usrp.headless_usrp(fast_integration=fast_integrationNoPulse, prefix=prefixTwo, samp_rate=sampleRate, vec_length=vecLength, freq=freqTwo)#take data
    tb2.start()
    time.sleep(integrationTime)
    tb2.stop()
    tb2.wait()

bandPassPlotter(tb1.recfile, tb2.recfile, vecLength, freqOne, freqTwo).plot()

movie = Popen("/bin/bash /home/odroid/Documents/dspira-master/grc-flowgraphs/movieMaker.sh", stdout=PIPE, shell=True)
output=movie.communicate()[0]
