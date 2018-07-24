import sys, time, os, datetime, argparse
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from bandPassPlotter import bandPassPlotter
from subprocess import Popen, PIPE

class whiteTelescope(object):
    def __init__(self, **options):
        self.options = options
        """
        self.options = {}
        self.options["separationLimit"] = 10#in degrees
        self.options["waitTime"] = 10#in seconds
        self.options["integrationTime"] = 280 # seconds
        self.options["fast_integrationPulse"] = 0.0005#when tapping the fast_integration output, in seconds
        self.options["freqOne"] = 1.4205e9
        self.options["freqTwo"] = 1.4202e9
        self.options["sampleRate"] = 3.0e6
        self.options["vecLength"] = 1024
        self.options["decimationFactor"] = 4
        self.options["source"] = "crab"
        self.options["folderOne"] = "/home/dspradio/grc_data/"
        self.options["folderTwo"] = "/home/dspradio/freq_shifts/"
        self.options["folderGiant"] = "/home/dspradio/giantPulses/"
        self.options["telescopeAZ"] = 180.0
        self.options["telescopeALT"] = 72.0
        self.options["targetRA"] = "05h43m32s"
        self.options["targetDEC"] = "22d00m52s"
        """
        #---------You shouldn't have to adjust anything below this line---------#
        self.options["fast_integrationNoPulse"] = 0.5 #when fast integration is not tapped [ie not used], in seconds  
        t = Time(datetime.datetime.utcnow())
        location = EarthLocation(lat=39.632858*u.deg, lon=-79.954926*u.deg, height=280*u.meter)
        #https://mail.scipy.org/pipermail/astropy/2015-March/003645.html
        pointing = SkyCoord(az=self.options["telescopeAZ"]*u.degree, alt=self.options["telescopeALT"]*u.degree, frame='altaz', \
                            location=location, obstime=t)
        target = SkyCoord(ra=self.options["targetRA"], dec=self.options["targetDEC"], frame='icrs')

        pointingRADEC =  pointing.transform_to('icrs')
        DECJ= pointingRADEC.dec.dms[0]*10000 + pointingRADEC.dec.dms[1]*100 + pointingRADEC.dec.dms[2]
        RAJ= pointingRADEC.ra.hms[0]*10000 + pointingRADEC.ra.hms[1]*100 + pointingRADEC.ra.dms[2]
        separationNow = target.separation(pointingRADEC).degree
        print("Telescope Object Separation = {0:.2f} deg".format(separationNow))
        print("Telescope Dec={0:.2f}".format(DECJ))
        print("Telescope RAJ={0:.2f}".format(RAJ))

        os.chdir("/home/odroid/gnuradio/lib/uhd/utils/share/uhd/images")#need to be in this directory for the ettus board to run

        if separationNow < self.options["separationLimit"]:
            import headless_usrp_giantpulse
            #from singlePulsePlotter import singlePulsePlotter
            tb1 = headless_usrp_giantpulse.headless_usrp_giantpulse(fast_integration=self.options["fast_integrationPulse"], \
                                                            prefix=self.options["folderOne"], samp_rate=self.options["sampleRate"],\
                                                            vec_length=self.options["vecLength"], freq=self.options["freqOne"],\
                                                            giant_prefix=self.options["folderGiant"], \
                                                            decimation_factor=self.options["decimationFactor"])
            #this is copied from gnuradio's main()
            tb1.start()
            time.sleep(self.options["integrationTime"])
            tb1.stop()
            tb1.wait()
    
            import filterbank as fb
            spdic = {}
            spdic["telescope_id"] = int(0)
            spdic["macnine_id"] = int(0)
            spdic["source_name"] = str(self.options["source"])
            spdic["barycentric"] = int(0)
            spdic["src_raj"] = float(RAJ)
            spdic["src_dej"] = float(DECJ)
            spdic["nbits"] = int(32)
            spdic["nchans"] = int(self.options["vecLength"]/self.options["decimationFactor"])
            spdic["nifs"] = int(1)
            spdic["fch1"] = float((self.options["freqOne"]-self.options["sampleRate"]/2.0+\
                                   self.options["sampleRate"]/(self.options["vecLength"]/self.options["decimationFactor"]))/10.0**6.0)
            spdic["foff"] = float(self.options["sampleRate"]/(self.options["vecLength"]/self.options["decimationFactor"]*10.0**6.0))
            spdic["tsamp"] = float(self.options["fast_integrationPulse"])
            spdic["tstart"] = float(Time(tb1.timeUTC).mjd)
            filterbank = fb.create_filterbank_file(tb1.giantout_bin.split('.bin')[0]+".fil", header=spdic, nbits=32)
            filterbank.close()
    
        else:
            import headless_usrp
            tb1 = headless_usrp.headless_usrp(fast_integration=self.options["fast_integrationNoPulse"], prefix=self.options["folderOne"],\
                                              samp_rate=self.options["sampleRate"], vec_length=self.options["vecLength"],\
                                              freq=self.options["freqOne"])
            tb1.start()
            time.sleep(self.options["integrationTime"])
            tb1.stop()
            tb1.wait()

        time.sleep(self.options["waitTime"])

        if separationNow < self.options["separationLimit"]:
            tb2 =  headless_usrp_giantpulse.headless_usrp_giantpulse(fast_integration=self.options["fast_integrationPulse"],\
                                                                     prefix=self.options["folderTwo"], \
                                                                     samp_rate=self.options["sampleRate"],\
                                                                     vec_length=self.options["vecLength"], freq=self.options["freqTwo"],\
                                                                     giant_prefix=self.options["folderGiant"], \
                                                                     decimation_factor=self.options["decimationFactor"])
            tb2.start()
            time.sleep(self.options["integrationTime"])
            tb2.stop()
            tb2.wait()
    
            spdic = {}
            spdic["telescope_id"] = int(0)
            spdic["macnine_id"] = int(0)
            spdic["source_name"] = str(self.options["source"])
            spdic["barycentric"] = int(0)
            spdic["src_raj"] = float(RAJ)
            spdic["src_dej"] = float(DECJ)
            spdic["nbits"] = int(32)
            spdic["nchans"] = int(self.options["vecLength"]/self.options["decimationFactor"])
            spdic["nifs"] = int(1)
            spdic["fch1"] = float((self.options["freqOne"]-self.options["sampleRate"]/2.0+\
                                   self.options["sampleRate"]/(self.options["vecLength"]/self.options["decimationFactor"]))/10.0**6.0)
            spdic["foff"] =  float(self.options["sampleRate"]/(self.options["vecLength"]/self.options["decimationFactor"]*10.0**6.0))
            spdic["tsamp"] = float(self.options["fast_integrationPulse"])
            spdic["tstart"] = float(Time(tb2.timeUTC).mjd)
    
            filterbank2 = fb.create_filterbank_file(tb2.giantout_bin.split('.bin')[0]+".fil", header=spdic, nbits=32)
            filterbank2.close()
            command2 = '/bin/cat ' +  tb2.giantout_bin + ' >> ' +  tb2.giantout_bin.split('.bin')[0]+".fil"
            fbmaker2 = Popen(command2, stdout=PIPE, shell=True)
            output2=fbmaker2.communicate()[0]
            fbmaker2.wait()
            remover2 = Popen('rm ' + tb2.giantout_bin, stdout=PIPE, shell=True)
            #output2=remover2.communicate()[0]
            mover2 = Popen('rsync -ah --remove-source-files '+tb2.giantout_bin.split('.bin')[0]+".fil " +\
                           'bowser:/hyrule/data/users/jwkania/odroid/giantPulses/',stdout=PIPE, shell=True)
            #output = mover2.communicate()[0]

            #moved here in hopes it doesn't mess with the sdr timing
            command = '/bin/cat ' +  tb1.giantout_bin + ' >> ' +  tb1.giantout_bin.split('.bin')[0]+".fil"
            fbmaker = Popen(command, stdout=PIPE, shell=True)
            output=fbmaker.communicate()[0]
            fbmaker.wait()
            remover = Popen('rm '+ tb1.giantout_bin, stdout=PIPE, shell=True)
            #output=remover.communicate()[0]
            #remover.wait()
            mover = Popen('rsync -ah --remove-source-files '+tb1.giantout_bin.split('.bin')[0]+".fil " +\
                          ' bowser:/hyrule/data/users/jwkania/odroid/giantPulses/', stdout=PIPE, shell=True)
            #output = mover.communicate()[0]
    
        else:
            tb2 = headless_usrp.headless_usrp(fast_integration=self.options["fast_integrationNoPulse"], prefix=self.options["folderTwo"],\
                                              samp_rate=self.options["sampleRate"], vec_length=self.options["vecLength"],\
                                              freq=self.options["freqTwo"])#take data
            tb2.start()
            time.sleep(self.options["integrationTime"])
            tb2.stop()
            tb2.wait()

        bandPassPlotter(tb1.recfile, tb2.recfile, self.options["vecLength"], self.options["freqOne"], self.options["freqTwo"]).plot()

        movie = Popen("/bin/bash /home/odroid/Documents/dspira-master/grc-flowgraphs/movieMaker.sh", shell=True, stdin=None,\
                      stdout=None, stderr=None)
        output=movie.communicate()[0]

if __name__ == "__main__":
    parser=argparse.ArgumentParser(
        description="Search GALFACTS for sources.",
        prog='find_sources.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    semi_opt = parser.add_argument_group('required arguments, defaults given.')
    semi_opt.add_argument('--separationLimit', type=float,
                           help="separation between tartget and telescope", default=10.0)
    semi_opt.add_argument('--waitTime', type=float,
                           help='wait time inbetween frequency switches', default=10.0)
    semi_opt.add_argument('--integrationTime', type=float,
                           help="integration time for spectra", default=280.0), 
    semi_opt.add_argument('--fast_integrationPulse', type=float,
                           help="integration to use when making filterbanks", default=0.0005)
    semi_opt.add_argument('--freqOne', type=float,
                           help="first frequency for frequency switiching", default=1.4205e9)
    semi_opt.add_argument('--freqTwo', type=float,
                           help="second frequency for frequency switiching", default=1.4202e9)
    semi_opt.add_argument('--sampleRate', type=float,
                           help="Rate which the USRP samples", default=3.0e6)
    semi_opt.add_argument('--vecLength', type=int,
                           help="Length of FFT", default=1024)
    semi_opt.add_argument('--decimationFactor', type=int,
                           help="Factor to reduce spectral resolution for pulse mode", default=4)
    #-----Below this line will be change to requard arguments in future versions-----#
    semi_opt.add_argument('--source', type=str,
                            help="name of source", default="crab")
    semi_opt.add_argument('--folderOne', type=str,
                           help="Folder to put first frequency.", default="/home/dspradio/grc_data/")
    semi_opt.add_argument('--folderTwo', type=str,
                           help="Folder to put second frequency.", default="/home/dspradio/freq_shifts/")
    semi_opt.add_argument('--folderGiant', type=str,
                           help="Folder to put pulses.", default="/home/dspradio/giantPulses/")
    semi_opt.add_argument('--telescopeAZ', type=float,
                           help="Telescope azimuth", default=180.0)
    semi_opt.add_argument('--telescopeALT', type=float,
                           help="Telescope altitude", default=72.0)
    semi_opt.add_argument('--targetRA', type=str,
                           help="Target's Right Ascension", default="05h43m32s")
    semi_opt.add_argument('--targetDEC', type=str,
                           help="Target's Declination", default="22d00m52s")
    args = vars(parser.parse_args())
    whiteTelescope(**args)
