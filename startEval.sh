#!/bin/bash
echo "starting cache DB"
x-terminal-emulator -T "cacheDB" -e "cd ../mobileClient/postgis_docker && docker-compose up" &
sleep 8
echo "starting map-excerpt-server"
x-terminal-emulator -T "MapExcerptServer (MES)" -e "cd ../mapExcerptServer && . venv/bin/activate &&./mapExcerptServer.py" &
echo "starting proxy before MES"
x-terminal-emulator -T "proxy before MES" -e "cd ../proxy && . venv/bin/activate &&./proxy.py --port 8083 --nomFile ../evaluation/nom_log.csv --mcFile ../evaluation/mc_log.csv --mesFile ../evaluation/mes_log.csv" &
echo "starting mobile client"
x-terminal-emulator -T "MobileClient (MC)" -e "cd ../mobileClient && . venv/bin/activate && ./client.py --no_expiration --mes http://localhost:8083/cacheArea" &
echo "starting proxy to MC and Nominatim"
x-terminal-emulator -T "first proxy" -e "cd ../proxy && . venv/bin/activate &&./proxy.py --nomFile ../evaluation/nom_log.csv --mcFile ../evaluation/mc_log.csv --mesFile ../evaluation/mes_log.csv" & 

tail -f mc_log.csv
