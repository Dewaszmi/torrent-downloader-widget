#!/usr/bin/env bash

DEFAULT_DOWNLOAD_PATH="$HOME/Downloads/Transmission-Downloads/"
TORRENT_FILE_DIR="./torrent_dir"

for i in $(ls ./torrent_dir); do
  if [[ $i == *.torrent ]]; then
    echo "Found $i, downloading.."
    transmission-remote -a "./torrent_dir/$i"
  fi
done
