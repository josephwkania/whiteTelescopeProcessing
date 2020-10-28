#!/usr/bin/env python2
"""Created by jwk june 2018"""
import matplotlib
matplotlib.use('Agg')#need to use Agg for non-gui printing
import h5py, csv, sys, argparse, imageio
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from glob import glob

class bandPassPlotter(object):
    def __init__(self, **options):
        self.options = options
        self.plot()
        self.movieMaker()
        
    def movieMaker(self):
        imageList = []
        for i in sorted(glob(self.options["folderImage"]+"*.png")):
            imageList.append(imageio.imread(i))
        kargs = {'loop':True, 'fps':5}
        imageio.mimsave(self.options["folderImage"]+self.options["UTC"]+".gif", imageList, 'GIF', **kargs)
        
    def plot(self):
        try:
            f = h5py.File(self.options["fileOne"],'r')
            spectrum = f['spectrum'][:].mean(axis=0)# get the spectrum data, mean flattens the data
            fileOne = True
        except:
            fileOne = False
            print("Didn't find fileOne: {0}".format(self.options["fileOne"]))
        try:
            switch = h5py.File(self.options["fileTwo"],'r')
            spectrum2 = switch['spectrum'][:].mean(axis=0)
            fileTwo = True
        except:
            fileTwo = False
            print("Didn't find fileTwo: {0}".format(self.options["fileTwo"]))
            
        if not fileOne and not fileTwo:
            print("Files are not there or are empty")
            sys.exit()
        elif not fileOne and fileTwo:#check to make sure first spectrum is there, it it isn't, plot the second file
            print("First file not present, plotting second")
            spectrum = spectrum2
            self.switch = False #if only both file are present do freq switching
            self.options["freqOne"] = self.options["freqTwo"]#makes sure csv has correct freq
            self.options["fileOne"] = self.options["fileTwo"]
            f = switch #redefine f, as to point to second file
        elif fileOne and not fileTwo:
            print("Second file not present, plotting first")
            diff = spectrum
            self.switch = False 
        else:#make sure the files are there before taking the difference
            print("Both files present, doing frequency switching")
            diff = spectrum - spectrum2
            self.switch = True
                
        def tick_function(x):#converts doppler to velocity
            V = (x/1420.4-1.0)*299972#km/s
            return ["%.1f" % z for z in V]

        def fitter(x, a, b, c, m, o):#for curve fitting
            offset = (self.options["freqOne"]-self.options["freqTwo"])/10.0**6.0
            return a*np.exp(-(x-b)**2.0/c**2.0)-a*np.exp(-(x-b-offset)**2.0/c**2.0)+m*x+o

        fstart = f.attrs['freq_start']       # get the start frequency
        #print fstart
        fstep = f.attrs['freq_step']         # get the stop frequency
        #print fstep
        freq = (np.arange(self.options["vecLength"])*fstep + fstart)/10.0**6.0# make an array of x-axis indices
        fig, ax1 = plt.subplots( figsize=(11,5))#use w/ twitter api
        ax2 = ax1.twiny()#allowes for top and bottom x-axis
        plt.tight_layout(pad=2.9)#use pad=2.9 if you don't care about 'counts' label, if you eant label pad=3.85
        ax1.set_xlabel('frequency [MHz] (w/ cntr={0}MHz)'.format(self.options["freqOne"]/10.0**6.0))
        ax1.get_xaxis().get_major_formatter().set_useOffset(False)#makes plt print out full axis
        ax2.set_xlabel('km/s (w/ cntr={0}MHz)'.format(self.options["freqOne"]/10.0**6.0))
        ax1.set_ylabel('Counts')
        #new_tick_locations = np.array([1420.0, 1420.25, 1420.4, 1420.5, 1420.75, 1421.0])
        new_tick_locations = np.array([1410.0, 1415.0, 1420.0, 1420.4, 1425.0, 1430.0, 1435.0])
        ax2.set_xticks(new_tick_locations)
        ax2.set_xticklabels(tick_function(new_tick_locations))
        plt.title("{0}, l={1:.1f}, b={2:.1f}".format(self.options["fileOne"].split('/')[-1], self.options["pointingGalacticL"], \
                                             self.options["pointingGalacticB"]),y=0.93)
        plt.rcParams['axes.formatter.useoffset'] = False
        #print("dem freq = {0}".format(len(freq)))
        #print("dem power = {0}".format(len(10.0*np.log10(spectrum.mean(axis=0)))))
        #print("max(power) = {0}".format(np.max(spectrum.mean(axis=0))))
        #print("max(power) = {0}".format(np.max(10.0*np.log10(spectrum.mean(axis=0)))))
        #plt.plot(freq, 10.0*np.log10(spectrum.mean(axis=0))) # log was taken before putting into the sink

        #plt.plot(freq,spectrum.mean(axis=0), freq, spectrum2.mean(axis=0), freq, diff.mean(axis=0))

        #ax1.set_xlim(xmin=1419.5,xmax=1421.5)
        if self.switch:
            #ax1.set_ylim([-14000,60000])#airspy
            #ax1.set_ylim([-15,90])#USRP
            ##plt.plot(freq,spectrum.mean(axis=0), label="Cntr1420.5MHz")
            ##plt.plot(freq, spectrum2.mean(axis=0),label="Cntr1420.2MHz")
            ##plt.plot(freq, diff.mean(axis=0),label="1420.5-1420.2")
            plt.plot(freq, spectrum, label="Cntr{0:.1f}MHz".format(self.options["freqOne"]/10.0**6.0))#divide by 10e6 to conver Hz to MHz
            plt.plot(freq, spectrum2, label="Cntr{0:.1f}MHz".format(self.options["freqTwo"]/10.0**6.0))
            plt.plot(freq, diff, label="{0:.1f}-{1:.1f}".format(self.options["freqTwo"]/10.0**6.0, self.options["freqOne"]/10.0**6.0))
            plt.legend(loc="upper right")
            #freqStartIndex = next(i for i, v in enumerate(freq) if v > 1420.15)#-900
            #freqEndIndex = next(i for i, v in enumerate(freq) if v > 1420.6)#+900
            cut=0.05#percent of bandpass to cut off [out of 1.0]
            trimmedFreq = freq[int(len(freq)*cut):int(len(freq)*(1.0-cut))]
            trimmedDiff = diff[int(len(freq)*cut):int(len(freq)*(1.0-cut))]
            trimmedSpectrum = spectrum[int(len(freq)*cut):int(len(freq)*(1.0-cut))]
            #plt.plot(trimmedFreq, trimmedDiff)
            maxLocation = np.argmax(trimmedDiff)
            self.options["trackingBoxWidth"] = 0.6e6
            guess = np.array([np.amax(trimmedDiff), trimmedFreq[maxLocation], 0.05, 0.0, 0.0])
            param_bounds = ([0, 1419.5,0.001, -15, -15], [np.inf, 1420.5, 1, 25, 25])
            try:
                popt, pcov = curve_fit(fitter, trimmedFreq,  trimmedDiff, guess)#, bounds=param_bounds)
            except:
                print("Fitting failed, using zeros for fit.")
                popt = [0, 0, 0.001, 0, 0]
            startIndex = int(maxLocation-self.options["trackingBoxWidth"]/2.0*self.options["vecLength"]/self.options["sampleRate"])
            endIndex = int(maxLocation+self.options["trackingBoxWidth"]/2.0*self.options["vecLength"]/self.options["sampleRate"])
            if startIndex < 0:#incase the box is at the end
                startIndex = 0
                endIndex = int(self.options["trackingBoxWidth"]/self.options["vecLength"]/self.options["sampleRate"])
            if endIndex > len(trimmedDiff) - 1:
                endIndex = len(trimmedDiff) - 1
                startIndex = int(endIndex - self.options["trackingBoxWidth"]/self.options["vecLength"]/self.options["sampleRate"])
            plt.axvline(x=trimmedFreq[startIndex])#plot the boundries of the box
            plt.axvline(x=trimmedFreq[endIndex])
            cleanedFlux = np.sum(trimmedSpectrum) - np.sum(trimmedDiff[startIndex:endIndex])
            print("Cleaned Integrated Flux = {0:.1f}".format(cleanedFlux))
            
            plt.plot(trimmedFreq, fitter(trimmedFreq, *popt))

            self.options["continuumFile"] = "{0}continuum.csv".format(self.options["folderCSV"])
            with open(self.options["continuumFile"],'a') as csvContinuum:
                csvContinuumWriter = csv.writer(csvContinuum, dialect='excel')
                #csvContinuum.write("#time,RA,DEC,integrationTime,cleanedFlux")
                csvContinuumWriter.writerow([self.options["fileOne"].split('/')[-1].split('_Drift.h5')[0], \
                                                                         self.options["RAinHour"], self.options["DECinDeg"], \
                                                                         self.options["integrationTime"], cleanedFlux])
                
            
            with open("{0}{1}.csv".format(self.options["folderCSV"], self.options["timeNow"]),'w') as csvfile:#writes files to csv 
                csvwriter = csv.writer(csvfile, dialect='excel')
                csvfile.write("#az={0},alt={1},start-freqOne={2}UTC,start-freqTwo={3}\n".format(self.options["telescopeAZ"], \
                                                                                                self.options["telescopeALT"],\
                                                                                                self.options["fileOne"].split('/')[-1].split('_D')[0], self.options["fileTwo"].split('/')[-1].split('_D')[0]))
                csvfile.write("#freqOne={0},freqTwo={1},sampleRate={2},numberOfFFTs={3}\n".format(self.options["freqOne"], \
                                                                                                  self.options["freqTwo"], \
                                                                                                  self.options["sampleRate"],\
                                                                                                  self.options["vecLength"]))
                csvfile.write("#source={0},integrationTime={1},waitTime={2}".format(self.options["source"], \
                                                                                    self.options["integrationTime"], \
                                                                                    self.options["waitTime"]))
                csvfile.write("#freq, counts@freq1, counts@freq2")
                csvwriter.writerows(zip(freq,spectrum,spectrum2))
            
        else:
            plt.plot(10.0*np.log10(spectrum.mean(axis=0)),label="Cntr{0:.1f}MHz".format(self.options["freqOne"]/10.0**6.0))
            #ax1.set_ylim([0,130000])#for airspy
            plt.legend(loc="upper right") 
            ax1.ticklabel_format(useOffset=False)

            #incase there is only one spectrum
            with open("{0}{1}.csv".format(self.options["folderCSV"],self.options["primarySpec.split"].split('.h5')[0]).split('/')[-1],'w') as csvfile:#writes files to csv 
                csvwriter = csv.writer(csvfile, dialect='excel')
                csvfile.write("#az={0},alt={1},start-freqOne={2}UTC\n".format(self.options["telescopeAZ"], \
                                                                              self.options["telescopeALT"],\
                                                                              self.options["fileOne"].split('/')[-1].split('_D')[0]))
                csvfile.write("#freqOne={0},sampleRate={1},numberOfFFTs={2}\n".format(self.options["freqOne"], \
                                                                                      self.options["sampleRate"],\
                                                                                      self.options["vecLength"]))
                csvfile.write("#source={0},integrationTime={1},waitTime={2}".format(self.options["source"], \
                                                                                    self.options["integrationTime"], \
                                                                                    self.options["waitTime"]))
                csv.write("#freq, counts@freq")
                csvwriter.writerows(zip(freq,spectrum))

            
        plt.savefig(self.options["folderImage"]+self.options["fileOne"].split('h5')[0].split('/')[-1]+'png', dpi=110) #use with twitter api
        plt.show()

         
if __name__ == "__main__":#if the program is run at top level
    parser=argparse.ArgumentParser(
        description="White Telescope Band Pass Plotter",
        prog='bandPassPlotter.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    required=parser.add_argument_group('required arguments:')
    required.add_argument('--fileOne',type=str,
                          help="first .h5 file",required=True)
    required.add_argument('--folderImage', type=str,
                          help="location of .png files", required=True)
    
    semi_opt=parser.add_argument_group('arguments set to defaults:')
    semi_opt.add_argument('--telescopeAZ',type=float,
                          help="Telescope pointing Azimuth", default=0.0)
    semi_opt.add_argument('--telescopeALT', type=float,
                          help="Telescope pointing Altitiude", default=0.0)
    semi_opt.add_argument('--source', type=str,
                          help="name of source telescope is looking at.",default="")
    semi_opt.add_argument('--integrationTime', type=float,
                          help="time data gathered", default=0.0)
    semi_opt.add_argument('--sampleRate', type=float,
                          help="Sample rate of USRP", default=3.0e6)
    semi_opt.add_argument('--freqOne',type=float,
                          help="Center frequency of first data set", default=1420.7e6)
    semi_opt.add_argument('--freqTwo', type=float,
                          help="Center frequency of second data set", default=1420.0e6)
    semi_opt.add_argument('--pointingGalacticL', type=float,
                          help="glactic l coordinate of souce [in degrees]", default=0.0)
    semi_opt.add_argument('--pointingGalacticB', type=float,
                          help="galactic b coordinate of source [in degrees]", default=0.0)
    optional=parser.add_argument_group('other optional arguments:')
    optional.add_argument('--fileTwo',type=str,nargs='+',
                          help="Second file to do frequency switching")

    args = vars(parser.parse_args())
    bandPassPlotter(**args)
