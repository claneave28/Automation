#!/bin/sh

location=fulljson.json
outputTxt=output.txt
OLDIFS=$IFS
IFS=$' \n'
array=`awk '{for(i=1;i<=NF;i++) if ($i=="Record") print $(i+1)}' $outputTxt | awk '{print substr($0, 2, length($0) - 2)}'`
b=($array)
for total in "${b[@]}";
    do
    lineitem=`awk '/query/{i++}i=="'$total'"{print NR; exit}' $location`
    echo "Record Error: #$total is located on line: $lineitem"
    done
 IFS=$OLDIFS