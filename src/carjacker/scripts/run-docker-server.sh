#!/usr/bin/env bash

if ! command -v docker >/dev/null 2>&1; then
  echo "Missing docker installation, install docker"
  exit 1
fi

API_DIR="$HOME/torrent-api"
mkdir -p "$API_DIR"
cd "$API_DIR" || exit

# Run a torrent site API server on http://localhost:8009
if [ ! -d Torrent-Api-py ]; then
  git clone https://github.com/Ryuk-me/Torrent-Api-py
fi
cd "Torrent-Api-py" || exit

if lsof -i :8009 >/dev/null 2>&1; then
  echo "Port 8009 is in use, try 'lsof -i :8009', 'pkill <PID>'"
  exit 1
fi

echo "Starting docker container"

docker compose up -d --build

until docker compose ps | grep "api-py"; do
  sleep 1
done

echo "Docker container running, API available at http://localhost:8009"

until curl -sSf http://localhost:8009 >/dev/null; do
  sleep 1
done

echo "API responsive"
