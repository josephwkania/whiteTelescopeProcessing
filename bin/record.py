#!/usr/bin/env python3

import time
import os
import datetime
import argparse
import getpass
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from white_radio import bandPassPlotter
from subprocess import Popen, PIPE


class whiteTelescope(object):
    def __init__(self, **options):
        self.options = options
        self.takeData()

    def takeData(self):
        self.options["UTC"] = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        base = (
            self.options["dirRoot"]
            + "/"
            + self.options["mode"]
            + "/"
            + self.options["source"]
            + "/"
            + self.options["UTC"]
        )
        self.options["folderOne"] = (
            base + "/freqOne/"
        )  # this is were the programs puts files
        self.options["folderTwo"] = base + "/freqTwo/"
        self.options["folderFilterbanks"] = base + "/filterbanks/"
        self.options["folderCSV"] = base + "/csv/"
        self.options["folderImage"] = base + "/images/"

        if not os.path.exists(
            self.options["folderOne"]
        ):  # check to see if folder exists, if not create it
            if self.options["verbose"]:
                print(
                    "No folder at {0}, making folder".format(self.options["folderOne"])
                )
            os.makedirs(self.options["folderOne"])
        if not os.path.exists(self.options["folderTwo"]):
            os.makedirs(self.options["folderTwo"])
        if not os.path.exists(self.options["folderFilterbanks"]):
            os.makedirs(self.options["folderFilterbanks"])
        if not os.path.exists(self.options["folderCSV"]):
            os.makedirs(self.options["folderCSV"])
        if not os.path.exists(self.options["folderImage"]):
            os.makedirs(self.options["folderImage"])

        logFileName = base + "/" + self.options["UTC"] + ".log"
        print(
            "Hello {0}, check {1} for your log file.".format(
                getpass.getuser(), logFileName
            )
        )
        log = open(logFileName, "a")  # dump the stout to this file
        # sys.stdout = log
        # sys.stderr = log

        self.options[
            "fast_integrationNoPulse"
        ] = 0.5  # when fast integration is not tapped [ie not used], in seconds
        t = Time(datetime.datetime.utcnow())
        location = EarthLocation(
            lat=39.632858 * u.deg, lon=-79.954926 * u.deg, height=280 * u.meter
        )
        # https://mail.scipy.org/pipermail/astropy/2015-March/003645.html
        pointing = SkyCoord(
            az=self.options["telescopeAZ"] * u.degree,
            alt=self.options["telescopeALT"] * u.degree,
            frame="altaz",
            location=location,
            obstime=t,
        )
        target = SkyCoord(
            ra=self.options["targetRA"], dec=self.options["targetDEC"], frame="icrs"
        )

        pointingRADEC = pointing.transform_to("icrs")
        galactic = pointingRADEC.galactic
        self.options["pointingGalacticL"] = galactic.l.degree
        self.options["pointingGalacticB"] = galactic.b.degree
        self.options["RAinHour"] = pointingRADEC.ra.hour
        self.options["DECinDeg"] = pointingRADEC.dec.degree
        self.options["DECJ"] = (
            pointingRADEC.dec.dms[0] * 10000
            + pointingRADEC.dec.dms[1] * 100
            + pointingRADEC.dec.dms[2]
        )
        self.options["RAJ"] = (
            pointingRADEC.ra.hms[0] * 10000
            + pointingRADEC.ra.hms[1] * 100
            + pointingRADEC.ra.dms[2]
        )
        self.options["telescopeRA"] = pointingRADEC.ra.to_string(u.hour)
        self.options["telescopeDEC"] = pointingRADEC.dec.to_string(
            u.degree, alwayssign=True
        )
        separationNow = target.separation(pointingRADEC).degree
        print(
            "Telescope-{0} Separation = {1:.2f} deg".format(
                self.options["source"], separationNow
            )
        )
        print("Telescope Dec={0}".format(self.options["telescopeDEC"]))
        print("Telescope RAJ={0}".format(self.options["telescopeRA"]))

        # os.chdir("/home/odroid/gnuradio/lib/uhd/utils/share/uhd/images")
        # need to be in this directory for the ettus board to run
        # os.chdir("/home/observer/whiteTelescopeProcessing/share/uhd/images")
        print(self.options["folderOne"])
        try:
            if True:  # separationNow < self.options["separationLimit"]:
                from white_radio import headless_usrp_giantpulse
                print(self.options["folderOne"])
                # from singlePulsePlotter import singlePulsePlotter
                tb1 = headless_usrp_giantpulse.headless_usrp_giantpulse(
                    fast_integration=self.options["fast_integrationPulse"],
                    prefix=self.options["folderOne"],
                    samp_rate=self.options["sampleRate"],
                    vec_length=self.options["vecLength"],
                    freq=self.options["freqOne"],
                    giant_prefix=self.options["folderFilterbanks"],
                    decimation_factor=self.options["decimationFactor"],
                )
                # this is copied from gnuradio's main()
                tb1.start()
                time.sleep(self.options["integrationTime"])
                tb1.stop()
                tb1.wait()

                from white_radio import filterbank as fb

                spdic = {}
                spdic["telescope_id"] = int(0)
                spdic["macnine_id"] = int(0)
                spdic["source_name"] = str(self.options["source"])
                spdic["barycentric"] = int(0)
                spdic["src_raj"] = float(self.options["RAJ"])
                spdic["src_dej"] = float(self.options["DECJ"])
                spdic["nbits"] = int(32)
                spdic["nchans"] = int(
                    self.options["vecLength"] / self.options["decimationFactor"]
                )
                spdic["nifs"] = int(1)
                spdic["fch1"] = float(
                    (
                        self.options["freqOne"]
                        - self.options["sampleRate"] / 2.0
                        + self.options["sampleRate"]
                        / (self.options["vecLength"] / self.options["decimationFactor"])
                    )
                    / 10.0 ** 6.0
                )
                spdic["foff"] = float(
                    self.options["sampleRate"]
                    / (
                        self.options["vecLength"]
                        / self.options["decimationFactor"]
                        * 10.0 ** 6.0
                    )
                )
                spdic["tsamp"] = float(self.options["fast_integrationPulse"])
                spdic["tstart"] = float(Time(tb1.timeUTC).mjd)
                filterbank = fb.create_filterbank_file(
                    tb1.giantout_bin.split(".bin")[0] + ".fil", header=spdic, nbits=32
                )
                filterbank.close()

                print("\nFinished First Frequency")

            else:
                from white_radio import headless_usrp

                tb1 = headless_usrp.headless_usrp(
                    fast_integration=self.options["fast_integrationNoPulse"],
                    prefix=self.options["folderOne"],
                    samp_rate=self.options["sampleRate"],
                    vec_length=self.options["vecLength"],
                    freq=self.options["freqOne"],
                )
                tb1.start()
                time.sleep(self.options["integrationTime"])
                tb1.stop()
                tb1.wait()

                print("Finished First Frequency")

            self.options["fileOne"] = tb1.recfile
            self.options["timeNow"] = tb1.timenow

        except Exception as e:
            print("Caught Exeption:{0}".format(e))
            print("freqOne Failed!, trying freqTwo.")
            self.options["fileOne"] = ""
            time.sleep(10)  # wait 10second to make sure usrp is done

        time.sleep(self.options["waitTime"])  # wait for USRP to stop talking data

        try:
            if True:  # separationNow < self.options["separationLimit"]:
                tb2 = headless_usrp_giantpulse.headless_usrp_giantpulse(
                    fast_integration=self.options["fast_integrationPulse"],
                    prefix=self.options["folderTwo"],
                    samp_rate=self.options["sampleRate"],
                    vec_length=self.options["vecLength"],
                    freq=self.options["freqTwo"],
                    giant_prefix=self.options["folderFilterbanks"],
                    decimation_factor=self.options["decimationFactor"],
                )
                tb2.start()
                time.sleep(self.options["integrationTime"])
                tb2.stop()
                tb2.wait()

                spdic = {}
                spdic["telescope_id"] = int(0)
                spdic["macnine_id"] = int(0)
                spdic["source_name"] = str(self.options["source"])
                spdic["barycentric"] = int(0)
                spdic["src_raj"] = float(self.options["RAJ"])
                spdic["src_dej"] = float(self.options["DECJ"])
                spdic["nbits"] = int(32)
                spdic["nchans"] = int(
                    self.options["vecLength"] / self.options["decimationFactor"]
                )
                spdic["nifs"] = int(1)
                spdic["fch1"] = float(
                    (
                        self.options["freqOne"]
                        - self.options["sampleRate"] / 2.0
                        + self.options["sampleRate"]
                        / (self.options["vecLength"] / self.options["decimationFactor"])
                    )
                    / 10.0 ** 6.0
                )
                spdic["foff"] = float(
                    self.options["sampleRate"]
                    / (
                        self.options["vecLength"]
                        / self.options["decimationFactor"]
                        * 10.0 ** 6.0
                    )
                )
                spdic["tsamp"] = float(self.options["fast_integrationPulse"])
                spdic["tstart"] = float(Time(tb2.timeUTC).mjd)

                filterbank2 = fb.create_filterbank_file(
                    tb2.giantout_bin.split(".bin")[0] + ".fil", header=spdic, nbits=32
                )
                filterbank2.close()

                print("\nFinished Second Frequency")

                command2 = (
                    "/bin/cat "
                    + tb2.giantout_bin
                    + " >> "
                    + tb2.giantout_bin.split(".bin")[0]
                    + ".fil"
                )
                fbmaker2 = Popen(command2, stdout=PIPE, shell=True)
                output2 = fbmaker2.communicate()[0]
                fbmaker2.wait()
                remover2 = Popen("rm " + tb2.giantout_bin, stdout=PIPE, shell=True)
                # output2=remover2.communicate()[0]
                # mover2 = Popen('rsync -ah --remove-source-files '+tb2.giantout_bin.split('.bin')[0]+".fil " +\
                #               'bowser:/hyrule/data/users/jwkania/odroid/giantPulses/',stdout=PIPE, shell=True)
                # output = mover2.communicate()[0]

                # moved here in hopes it doesn't mess with the sdr timing
                command = (
                    "/bin/cat "
                    + tb1.giantout_bin
                    + " >> "
                    + tb1.giantout_bin.split(".bin")[0]
                    + ".fil"
                )
                fbmaker = Popen(command, stdout=PIPE, shell=True)
                output = fbmaker.communicate()[0]
                fbmaker.wait()
                remover = Popen("rm " + tb1.giantout_bin, stdout=PIPE, shell=True)
                # output=remover.communicate()[0]
                # remover.wait()
                # mover = Popen('rsync -ah --remove-source-files '+tb1.giantout_bin.split('.bin')[0]+".fil " +\
                #              ' bowser:/hyrule/data/users/jwkania/odroid/giantPulses/', stdout=PIPE, shell=True)
                # output = mover.communicate()[0]

            else:
                tb2 = headless_usrp.headless_usrp(
                    fast_integration=self.options["fast_integrationNoPulse"],
                    prefix=self.options["folderTwo"],
                    samp_rate=self.options["sampleRate"],
                    vec_length=self.options["vecLength"],
                    freq=self.options["freqTwo"],
                )  # take data
                tb2.start()
                time.sleep(self.options["integrationTime"])
                tb2.stop()
                tb2.wait()

                print("\nFinished Second Frequency")

            self.options["fileTwo"] = tb2.recfile

        except Exception as e:
            print("Caught Exeption:{0}".format(e))
            print("freqTwo failed!")
            self.options["fileTwo"] = ""
        print(self.options)
        bandPassPlotter.bandPassPlotter(**self.options)

        # movie = Popen("/bin/bash /home/odroid/Documents/dspira-master/grc-flowgraphs/movieMaker.sh", shell=True, stdin=None,\
        #               stdout=None, stderr=None)
        # output=movie.communicate()[0]

        for i in self.options:
            print("{0: >23}:\t{1}".format(i, self.options[i]))
        print("")  # nice spacing
        log.close  # close log file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="White Telescope Controller",
        prog="record.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    semi_opt = parser.add_argument_group("required arguments [test defaults given].")
    semi_opt.add_argument(
        "--separationLimit",
        type=float,
        help="separation between tartget and telescope",
        default=10.0,
    )
    semi_opt.add_argument(
        "--waitTime",
        type=float,
        help="wait time inbetween frequency switches [sec]",
        default=10.0,
    )
    semi_opt.add_argument(
        "--integrationTime",
        type=float,
        help="integration time for spectra [sec]",
        default=280.0,
    ),
    semi_opt.add_argument(
        "--fast_integrationPulse",
        type=float,
        help="integration to use when making filterbanks [sec]",
        default=0.0005,
    )
    semi_opt.add_argument(
        "--freqOne",
        type=float,
        help="first frequency for frequency switiching [Hz]",
        default=1.4207e9,
    )
    semi_opt.add_argument(
        "--freqTwo",
        type=float,
        help="second frequency for frequency switiching [Hz]",
        default=1.4200e9,
    )
    semi_opt.add_argument(
        "--sampleRate", type=float, help="Rate which the USRP samples [/s]", default=40.0e6
    )
    semi_opt.add_argument("--vecLength", type=int, help="Length of FFT/number of channels", default=1024)
    semi_opt.add_argument(
        "--decimationFactor",
        type=int,
        help="Factor to reduce number of channels for pulse mode",
        default=4,
    )
    semi_opt.add_argument(
        "--dirRoot",
        type=str,
        help="Base of the directory to put the files.",
        default="/data",
    )

    # -----Below this line will be change to requard arguments in future versions-----#
    semi_opt.add_argument("--source", type=str, help="name of source", default="drift")
    # semi_opt.add_argument('--folderOne', type=str,
    #                       help="Folder to put first frequency.", default="/home/dspradio/grc_data/")
    # semi_opt.add_argument('--folderTwo', type=str,
    #                       help="Folder to put second frequency.", default="/home/dspradio/freq_shifts/")
    # semi_opt.add_argument('--folderGiant', type=str,
    #                       help="Folder to put pulses.", default="/home/dspradio/giantPulses/")
    semi_opt.add_argument(
        "--mode", type=str, help="pulsar or coninuum", default="continuum"
    )
    semi_opt.add_argument(
        "--telescopeAZ", type=float, help="Telescope azimuth", default=0.0
    )
    semi_opt.add_argument(
        "--telescopeALT", type=float, help="Telescope altitude", default=0.0
    )
    semi_opt.add_argument(
        "--targetRA", type=str, help="Target's Right Ascension", default="0h0m0s"
    )
    semi_opt.add_argument(
        "--targetDEC", type=str, help="Target's Declination", default="0d0m0s"
    )

    optional = parser.add_argument_group("other optional arguments:")
    optional.add_argument(
        "-v", "--verbose", help="verbose analysis", action="store_true"
    )

    args = vars(parser.parse_args())
    whiteTelescope(**args)
