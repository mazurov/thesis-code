#!/bin/sh

sleep $1
ssh -x lxplus -t "source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/prod"\
"/InstallArea/scripts/LbLogin.sh;"\
". /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/LBSCRIPTS_v7r8p2"\
"/InstallArea/scripts/SetupProject.sh Bender v22r11;"\
"cd ~/thesis-code;"\
"~/thesis-code/fit.py --decay=$2 --year=$3 --ptbegin=$4 --ptend=$5 --profile=$6;"\
"sleep 20"
