#!/bin/bash

#sleep 572
#for f in /home/dspradio/grc_data/*.h5; do
#    /usr/bin/python /home/dspradio/grc_data/plotter.py $f 
#done

rm /home/dspradio/grc_data/"$(date +%Y-%m-%d).mp4"

/usr/bin/ffmpeg -pattern_type glob -framerate 2 -i "/home/dspradio/grc_data/$(date +%Y-%m-%d)*_Drift.png" "/home/dspradio/grc_data/$(date +%Y-%m-%d).mp4" 


rm /home/dspradio/grc_data/"$(date +%Y-%m-%d).gif" 
rm /home/dspradio/grc_data/palette.png 

/usr/bin/ffmpeg -i /home/odroid/Documents/dspira-master/grc-flowgraphs/platteCreator.png -vf palettegen  /home/dspradio/grc_data/palette.png

/usr/bin/ffmpeg -pattern_type glob -framerate 2 -thread_queue_size 256 -i "/home/dspradio/grc_data/$(date +%Y-%m-%d)*_Drift.png"  -i /home/dspradio/grc_data/palette.png -lavfi paletteuse /home/dspradio/grc_data/$(date +%Y-%m-%d).gif
