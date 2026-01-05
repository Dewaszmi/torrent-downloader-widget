#!/usr/bin/env bash

# Install Jackett as a systemd service (from https://github.com/Jackett/Jackett documentation)
cd /opt
f=Jackett.Binaries.LinuxAMDx64.tar.gz
sudo wget -Nc https://github.com/Jackett/Jackett/releases/latest/download/"$f"
sudo tar -xzf "$f"
sudo rm -f "$f"
cd Jackett*
sudo chown $(whoami):$(id -g) -R "/opt/Jackett"

# Installs and enables systemctl jackett service
sudo ./install_service_systemd.sh
systemctl status jackett.service
cd -
echo -e "\nVisit http://127.0.0.1:9117"
