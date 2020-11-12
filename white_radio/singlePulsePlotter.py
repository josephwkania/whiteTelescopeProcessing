"""Created July 2018 by jwk"""
import matplotlib

# matplotlib.use('Agg')
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt


class singlePulsePlotter(object):
    def __init__(self, *args):
        self.inputFile = args[0]
        self.timeRes = 0.001  # time between samples, in seconds
        if len(args) > 1:
            self.timeRes = args[1]

    def plot(self):
        f = h5py.File("{0}".format(self.inputFile), "r")
        # print list(f.attrs)         # check the metadata attributes
        # print list(f.attrs.items()) # check the metadata attributes and their values
        # print f.items()             # list the datasets in the file

        spectrum = f["spectrum"][:]  # get the spectrum data
        # print len(spectrum)
        fstart = f.attrs["freq_start"]  # get the start frequency
        # print fstart
        # fstep = f.attrs['freq_step']         # get the stop frequency
        # print fstep

        fig, ax1 = plt.subplots(figsize=(11, 5))  # use w/ twitter api
        plt.tight_layout(
            pad=2.9
        )  # use pad=2.9 if you don't care about 'counts' label, if you eant label pad=3.85
        ax1.set_xlabel("time [s]")
        ax1.set_ylabel("Counts")
        plt.title(format(self.inputFile.split("/")[-1]), y=0.93)
        plt.rcParams["axes.formatter.useoffset"] = False
        spectrumFlat = spectrum.flatten()
        plt.plot(np.arange(0, len(spectrumFlat)) * self.timeRes, spectrumFlat)
        ax1.ticklabel_format(useOffset=False)

        plt.savefig(
            self.inputFile.split("h5")[0] + "png", dpi=110
        )  # use with twitter api


if __name__ == "__main__":  # if its run from the top level
    singlePulsePlotter(sys.argv[1]).plot()
