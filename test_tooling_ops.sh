#!/bin/sh

#----#... that's not a real module is it?
module load HOOEY

#here's more garbage characters to see if i can confuse this
####@$%^#%^&#%^&#%*##$%!



### THIS IS A FAKE SCRIPT FOR TESTING PURPOSES!!!!
mv stuffA STUFFB

cp stuff2 stuffEXCESSIVE


mv gobbledeGuk hoo_haa

tar czvf sumthin.tgz thisdirdoesntexist/*.FOO

if tar zxvf sumthin.tgz; then
	echo "hello! success!"
else
	echo "hello! failure"
fi
