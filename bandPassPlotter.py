"""Created by jwk june 2018"""
import matplotlib
matplotlib.use('Agg')#need to use Agg for non-gui printing
import h5py, csv, sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class bandPassPlotter(object):
    def __init__(self, *args):
        self.flength = 1024#default value
        self.primaryFreq = 1420.5
        self.secondaryFreq = 1420.2
        self.primarySpec = args[0]
        if len(args) >= 2: 
            self.secondarySpec = args[1]
            self.switch = True
        if len(args) >= 3:
            self.flength = args[2]
            self.primaryFreq = args[3]/10.0**6.0
            self.secondaryFreq = args[4]/10.0**6.0
            

    def plot(self):
        f = h5py.File(self.primarySpec,'r')
        #print list(f.attrs)         # check the metadata attributes
        #print list(f.attrs.items()) # check the metadata attributes and their values
        #print f.items()             # list the datasets in the file
        #extract the spectrum data and
        spectrum = f['spectrum'][:].mean(axis=0)# get the spectrum data, mean flattems the data
        if self.switch:
            switch = h5py.File(self.secondarySpec,'r')
            #print list(switch.attrs)         # check the metadata attributes
            #print list(switch.attrs.items()) # check the metadata attributes and their values
            #print switch.items()             # list the datasets in the file
            spectrum2 = switch['spectrum'][:].mean(axis=0)
            try:#try catch incase the spectra have different dimensions, should be a
                #a problem because we take the mean first
                diff = spectrum - spectrum2 
            except ValueError:
                print("I can't take the difference of the spectra")
                diff = spectrum

        def tick_function(x):#converts doppler to velocity
            V = (x/1420.4-1.0)*299972#km/s
            return ["%.1f" % z for z in V]

        def fitter(x, a, b, c, m, o):#for curve fitting
            return a*np.exp(-(x-b)**2.0/c**2.0)-a*np.exp(-(x-b+0.5)**2.0/c**2.0)+m*x+o

        fstart = f.attrs['freq_start']       # get the start frequency
        #print fstart
        fstep = f.attrs['freq_step']         # get the stop frequency
        #print fstep
        freq = (np.arange(self.flength)*fstep + fstart)/10.0**6.0# make an array of x-axis indices
        fig, ax1 = plt.subplots( figsize=(11,5))#use w/ twitter api
        ax2 = ax1.twiny()#allowes for top and bottom x-axis
        plt.tight_layout(pad=2.9)#use pad=2.9 if you don't care about 'counts' label, if you eant label pad=3.85
        ax1.set_xlabel('frequency [MHz] (w/ cntr=1420.5MHz)')
        ax1.get_xaxis().get_major_formatter().set_useOffset(False)#makes plt print out full axis
        ax2.set_xlabel('km/s (w/ cntr=1420.5MHz)')
        ax1.set_ylabel('Counts')
        new_tick_locations = np.array([1420.0, 1420.25, 1420.4, 1420.5, 1420.75, 1421.0])
        ax2.set_xticks(new_tick_locations)
        ax2.set_xticklabels(tick_function(new_tick_locations))
        plt.title(format(self.primarySpec.split('/')[-1]),y=0.93)
        plt.rcParams['axes.formatter.useoffset'] = False
        #print("dem freq = {0}".format(len(freq)))
        #print("dem power = {0}".format(len(10.0*np.log10(spectrum.mean(axis=0)))))
        #print("max(power) = {0}".format(np.max(spectrum.mean(axis=0))))
        #print("max(power) = {0}".format(np.max(10.0*np.log10(spectrum.mean(axis=0)))))
        #plt.plot(freq, 10.0*np.log10(spectrum.mean(axis=0))) # log was taken before putting into the sink

        #plt.plot(freq,spectrum.mean(axis=0), freq, spectrum2.mean(axis=0), freq, diff.mean(axis=0))

        ax1.set_xlim(xmin=1419.5,xmax=1421.5)
        if self.switch:
            #ax1.set_ylim([-14000,60000])#airspy
            ax1.set_ylim([-15,90])#USRP
            #plt.plot(freq,spectrum.mean(axis=0), label="Cntr1420.5MHz")
            #plt.plot(freq, spectrum2.mean(axis=0),label="Cntr1420.2MHz")
            #plt.plot(freq, diff.mean(axis=0),label="1420.5-1420.2")
            plt.plot(freq, spectrum, label="Cntr{0:.1f}MHz".format(self.primaryFreq))
            plt.plot(freq, spectrum2, label="Cntr{0:.1f}MHz".format(self.secondaryFreq))
            plt.plot(freq, diff, label="{0:.1f}-{1:.1f}".format(self.primaryFreq, self.secondaryFreq))
            plt.legend(loc="upper right")
            #freqStartIndex = next(i for i, v in enumerate(freq) if v > 1420.15)-900
            #freqEndIndex = next(i for i, v in enumerate(freq) if v > 1420.6)+900
            #plt.plot( freq[freqStartIndex:freqEndIndex],diff.mean(axis=0)[freqStartIndex:freqEndIndex])
            #popt, pcov = curve_fit(fitter, freq[freqStartIndex:freqEndIndex].mean(axis=0),  diff[freqStartIndex:freqEndIndex])
            #freqFitX = np.linespace(1420.15,1420.6,1000)
            #plt.plot(freqFitX, fitter(freqFitX, *popt))
        else:
            plt.plot(10.0*np.log10(spectrum.mean(axis=0)),label=="Cntr{0:.1f}MHz".format(self.primaryFreq))
            #ax1.set_ylim([0,130000])#for airspy
            plt.legend(loc="upper right") 
            ax1.ticklabel_format(useOffset=False)

        plt.savefig(self.primarySpec.split('h5')[0]+'png', dpi=110) #use with twitter api
        plt.show()

        with open("{0}csv".format(self.primarySpec.split('h5')[0]),'w') as csvfile:#writes files to csv 
            csvwriter = csv.writer(csvfile, dialect='excel')
            csvfile.write("#az=+180, alt=+72, time={0}UTC\n".format(self.primarySpec.split('/')[-1].split('_D')[0]))
            csvwriter.writerows(zip(freq,spectrum,spectrum2))

         
if __name__ == "__main__":#if the program is run at top level
    print "In main"
    if len(sys.argv) == 1:
        bandPassPlotter(sys.argv[1]).plot()
    elif len(sys.argv) == 2:
        bandPassPlotter(sys.argv[1], sys.argv[2]).plot()
    else:
        print("I can't handle this many arguments in command line mode!")
