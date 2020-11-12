#!/usr/bin/python
"""Created by jwk july 2018"""

import matplotlib
matplotlib.use("Agg")  # need to use Agg for non-gui printing
import matplotlib.pyplot as plt
import csv
import argparse
# from datetime import datetime

class continuumPlotter(object):
    def __init__(self, **options):
        self.options = options
        self.plot()

    def plot(self):
        time = []
        RA = []
        DEC = []
        integrationTime = []
        cleanedFlux = []
        with open(self.options["continuumFile"], "r") as csvFile:
            reader = csv.reader(csvFile, delimiter=",")
            # from bandPassPlotter.py the format of the files is #time,RA,DEC,integrationTime,cleanedFlux
            for r in reader:
                print len(r)
                time.append(r[0])  # datetime.strptime(r[0], "%Y-%m-%d_%H.%M.%S"))
                RA.append(r[1])
                DEC.append(r[2])
                integrationTime.append((r[3]))
                cleanedFlux.append((r[4]))

        print (time)
        print (RA)
        print (DEC)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="White Telescope Continuum Plotter.",
        prog="continuumPlotter.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    required = parser.add_argument_group("required arguments:")
    required.add_argument(
        "--continuumFile", type=str, help="field to cluster", required=True
    )
    args = vars(parser.parse_args())
    continuumPlotter(**args)
