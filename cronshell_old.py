#!/home/odroid/gnuradio/setup_env.sh
import sys,time, headless_usrp, headless_usrp_freqshift, os 
from subprocess import call

#call(["source", "/home/odroid/gnuradio/setup_env.sh"], shell=True)#need to source this to make python happy
os.chdir("/home/odroid/gnuradio/lib/uhd/utils/share/uhd/images")#need to be in this directory for the ettus board to run

headless_usrp.main() #take data

time.sleep(31)#wait

headless_usrp_freqshift.main()#take data

time.sleep(3)

call(['/bin/bash','/home/dspradio/grc_data/plotter.sh'])
