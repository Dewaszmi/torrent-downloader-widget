#!/usr/bin/env bash

API_DIR="$HOME/torrent-api"
mkdir - p$API_DIR
cd $API_DIR

if ! command -v docker >/dev/null 2>&1
then
  echo "Missing docker installation, install docker"
  exit 1
fi

# Run a unofficial torrent site API server on http://localhost:8009
if [ ! -d Torrent-Api-py ]; then
  git clone https://github.com/Ryuk-me/Torrent-Api-py
fi
cd Torrent-Api-py

if lsof -i :8009 >/dev/null 2>&1; then
  echo "Port 8009 is in use, try 'lsof -i :8009', 'pkill <PID>'"
  exit 1
fi

docker compose up -d --build
echo "test"

until docker compose ps | grep "api-py" | grep -q running; do
  echo "test"
  sleep 0.5
  echo -n "."
done

echo "Container running, api available at http://localhost:8009"
