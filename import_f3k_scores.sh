#!/usr/bin/env bash

# Import scores from f3k files
# You give it a toplevel folder with contests and it generates the needed csv.

# Need to find a a way to automate that shitty f3kscore appken

folder=$1
out=$2

f3kscore="java -jar /Users/johan/Projects/f3k/f3kscore/F3KScore_v8.9_patched/f3kscore_v8.9.jar"

#find $folder -name "*.f3k" | while read file
#do
#  echo "Process $file"
#  $f3kscore "$file"
#done

find $folder -name "Totals.csv" | while read totals
do
  contest=$(basename $(dirname $totals))
  echo $contest
  cat $totals | ./convert_f3kscore.pl > data/BK/$contest.csv
done
