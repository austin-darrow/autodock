#!/bin/bash

# set system variables.  You can remove this if they are set elsewhere.
OUT_DIR="./out"
TEMP_RESULTS_PREFIX="./out/tempResults"
REPORT_FILE="topResults.txt"
NUM_TOP_RESULTS=1000
TOP_RESULTS_DIR="./results"

# make our own die function
die() { echo "$@" 1>&2 ; exit 1; }


# we need exactly 2 input arguments
if [[ $# -lt 1 || $# -gt 1 || $1 == '-h' ]]; then
  echo "Usage: paramgen ligands.txt"
  echo "ligands.txt is expected to be the absolute paths of all the ligands to scan."
fi

paramlist="paramlist"
while [ -f $paramlist ]; do
  # check if $PS1 is not set to decide if this is an interactive shell
  if [ -z $PW1 ]; then
    # this is not an interactive shell. just backup paramlist and replace it
    mv $paramlist ${paramlist}.bak.$(date +%Y-%m-%d_%H%M%S)
  else
    # if this is an interactive shell, let the user pick the filename
    echo "The file \"${paramlist}\" already exists? Pick a new filename or press Enter to overwrite."
    read input
    if [ "$input" == "" ];then
      rm -f $paramlist
    else
      paramlist=$input
    fi
  fi
done

# Error Checking 
ligands=$1

if [ ! -f $ligands ]; then
  die "The file list of ligands $ligands does not exist.\n"
fi

# Make output directories
if [ ! -d out ]; then
  mkdir ./out
else
  echo "Is it okay to remove and overwrite the output directory? (yes/no): "
  read input
  if [ `echo $input | tr [:upper:] [:lower:]` == "yes" ]; then
    rm -rf ./out/*
  else
    die "Error: This script requires a local out directory."
  fi
fi

# Make results directory
if [ ! -d results ]; then
  mkdir ./results
else
  echo "Is it okay to remove and overwrite the results directory? (yes/no): "
  read input
  if [ `echo $input | tr [:upper:] [:lower:]` == "yes" ]; then
    rm -rf ./results/*
  else
    die "Error: This script requires a local results directory."
  fi
fi


# setup directory structure
my_time="/usr/bin/time -o timings.txt --append perl -e 'alarm shift @ARGV; exec @ARGV' 300"
my_grep=`which grep`
my_awk=`which awk`

while read line; do
  subdir=`basename ${line%/*}`
  if [ ! -d ./out/$subdir ]; then
    mkdir ./out/$subdir
  fi
  filename=`basename $line`

  my_vina_command="vina --config config.in --ligand $line --out ./out/${subdir}/${filename} > /dev/null"
  # Get the current ligand score.
  # the lowest (i.e. best) score should always be the first one listed
  # JMF: it looks like the score is always on the second line.  This step could be sped up  I think.
  #my_postprocessing="score=\$($my_grep -m 1 \"REMARK VINA RESULT:\" ./out/${subdir}/${filename} | $my_awk '{ print \$4 }'); echo \"./out/${subdir}/${filename} \$score\" >> $TEMP_RESULTS_PREFIX\$LAUNCHER_TSK_ID"
  # Add a catch in case the ligand didn't finish in the time allowed
  my_postprocessing="if [[ -e \"./out/${subdir}/${filename}\" ]]; then score=\$($my_grep -m 1 \"REMARK VINA RESULT:\" ./out/${subdir}/${filename} | $my_awk '{ print \$4 }'); echo \"./out/${subdir}/${filename} \$score\" >> $TEMP_RESULTS_PREFIX\$LAUNCHER_TSK_ID; fi"

  echo "$my_time $my_vina_command; $my_postprocessing" >> $paramlist
done < $ligands



