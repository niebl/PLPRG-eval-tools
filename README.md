# The Evaluation Tools

Tools that were used for simulation and evaluation can be found in the directory "evaluation tools".

The evaluation tools are released under the MIT-License (see license.txt)

## startEval.sh

tool that is used to start all the elements of the simulation environment. Includes the LPPM with it's reverse proxies, as well as a Nominatim instance with a reverse proxy. Please ensure all ports needed by the applications are freed, and all scripts have properly set up venvs

The MC requires a working docker installation for the container of the cache-database.

## runTrajectory.sh

Tool that is used to simulate the behavior of the mobile user. Accepts csv-formatted data from stdin.

requires the LPPM, Nominatim, and reverse proxies to be running.

requires "csvkit" https://csvkit.readthedocs.io/en/latest/tutorial/1_getting_started.html#installing-csvkit

## csvToGeoJSON.py

Tool that transforms a csv-file into a geoJSON string suitable for the inference engine. accepts csv-data via stdin

## dataProcessing.r

R-Script that evaluates the data and calculates correctness of the MC results. To be run in the same directory as the acaquired data.

requires the files mc_join.csv, nom_join.csv and mes_log.csv

requires R-packages rjson and stringr

## Inference/inferenceEngine.py

python port of the inference engine implemented in https://github.com/sitcomlab/simport-learning-app

requirements appended in `requirements.txt`

accepts geoJSON formatted data via stdin

