#!/bin/bash

#require csvkit: https://csvkit.readthedocs.io/en/latest/tutorial/1_getting_started.html#installing-csvkit

filename=$1
firstLine=true

if [ -z $filename ]; then
    cat - | csvcut -c timestamp_ms,lat,lon | while read line; do
        if [ "$firstLine" = true ] ; then
            firstLine=false
            continue
        fi

        #split each line
        IFS="," read -ra values <<< "$line"

        timestamp=${values[0]}
        lat=${values[1]}
        lon=${values[2]}

        url="http://localhost:8082/mobileClient?lat=${lat}&lon=${lon}&time=${timestamp}" 
        res=$(curl $url)
        echo "|${res}|" >> mc_results.csv
        #echo "" >> mc_results.csv
    
        url="http://localhost:8082/reverse?lat=${lat}&lon=${lon}&time=${timestamp}"
        res=$(curl $url)
        echo "|${res}|" >> nom_results.csv
        #echo "" >> nom_results.csv

    done

else
    csvcut -c timestamp_ms,lat,lon $filename | while read line; do
        if [ "$firstLine" = true ] ; then
            firstLine=false
            continue
        fi

        #split each line
        IFS="," read -ra values <<< "$line"

        timestamp=${values[0]}
        lat=${values[1]}
        lon=${values[2]}

        url="http://localhost:8082/mobileClient?lat=${lat}&lon=${lon}&time=${timestamp}"
        #echo $url 
        curl $url
        echo ""

    done
fi
