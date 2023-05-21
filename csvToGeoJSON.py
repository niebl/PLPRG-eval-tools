#!/usr/bin/python3
import json
import argparse,sys
import csv

def main():
    content = None

    if not args["csv"]:
        stdin = ""
        #firstLine to make concatenation of several csv possible.
        firstLine = None
        i = 0
        for line in sys.stdin:
            if i == 0:
                firstLine = line
                stdin += line
            elif line != firstLine:
                stdin += line
            i += 1
        content = csv.DictReader(stdin.splitlines(), delimiter=DELIM)
    else:
        inputFile = open(args["csv"], "r")
        content = csv.DictReader(inputFile, delimiter=DELIM)

    if content is None:
        print("please enter input file")
        return
    
    time = []
    timestamp = []
    lonLat = []
    accuracy = []
    speed = []

    #check which keys exist
    dictKeys = next(content).keys()
    keys = ""
    for line in dictKeys:
        keys += line + ","

    for line in content:
        #get time from time or timestamp_m
        time = None
        if "timestamp_ms" in keys:
            time = line["timestamp_ms"]
        elif "timestamp" in keys:
            time = line["timestamp"]
        elif "time" in keys:
            time = line["time"]
        else:
            time = ""

        timestamp.append(time)
        lonLat.append([float(line["lon"]),float(line["lat"])])
        accuracy.append(line["accuracy"]) if "accuracy" in keys else accuracy.append("")
        speed.append(line["speed"]) if "speed" in keys else speed.append("")

    geoObj = {
        "type": "FeatureCollection",
        "features" : [
            {
                "type":"Feature",
                "properties":{
                    "timestamp": timestamp,
                    "accuracy": accuracy,
                    "speed": speed
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": lonLat
                }
            }
        ]
    }   
    indent = int(args["indent"]) if args["indent"] else None
    geojson = json.dumps(geoObj, indent=indent)
    print(geojson)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--csv", help="link to csv-file")
    parser.add_argument("--out", help="output file")
    parser.add_argument("--indent", help="indent")
    parser.add_argument("--delim", help="delimiter")



    args = parser.parse_args()
    args = vars(args)

    DELIM = args["delim"] if args["delim"] else "," 

    main()