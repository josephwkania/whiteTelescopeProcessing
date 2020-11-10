#!/bin/bash

for d in /home/usrs/*/*/; do
    cd $d #cd into the dir
    tar -czf UTC$(date +%Y-%m-%d -d "yesterday").tar.gz $(date +%Y-%m-%d -d "yesterday") #tar yesterdays file
    rm -r $(date +%Y-%m-%d -d "yesterday") #remove the original file
done
