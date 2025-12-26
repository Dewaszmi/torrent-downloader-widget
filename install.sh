#!/usr/bin/env bash

# Set some colors for output messages
OK="$(tput setaf 2)[OK]$(tput sgr0)"
ERROR="$(tput setaf 1)[ERROR]$(tput sgr0)"
NOTE="$(tput setaf 3)[NOTE]$(tput sgr0)"
INFO="$(tput setaf 4)[INFO]$(tput sgr0)"
WARN="$(tput setaf 1)[WARN]$(tput sgr0)"
CAT="$(tput setaf 6)[ACTION]$(tput sgr0)"
MAGENTA="$(tput setaf 5)"
ORANGE="$(tput setaf 214)"
WARNING="$(tput setaf 1)"
YELLOW="$(tput setaf 3)"
GREEN="$(tput setaf 2)"
BLUE="$(tput setaf 4)"
SKY_BLUE="$(tput setaf 6)"
RESET="$(tput sgr0)"

echo "${INFO} INSTALLING TORRENT UTILITY SOFTWARE"

is_installed_rpm() {
    rpm -q "$1" &>/dev/null
}

printf "\n%.0s" {1..2}
echo "${ORANGE}Act I: ${RESET}Installing ${SKY_BLUE}Transmission"
printf "\n%.0s" {1..1}

transmission_packages=(
  transmission
  transmission-cli
  transmission-daemon
)
missing=()

for pkg in "${transmission_packages[@]}"; do
  if is_installed_rpm "$pkg"; then
    echo "Found ${GREEN}"$pkg" ${RESET}installation."
  else
    echo "${WARNING}$pkg installation not found.."
    missing+=("$pkg")
  fi
done

for missing_pkg in "${missing[@]}"; do
  echo "${INFO} Installing $pkg"
  sudo dnf install $pkg$ -y
done

echo "${OK} Installation completed."

printf "\n%.0s" {1..2}
echo "${ORANGE}Act II: ${RESET}Setting up ${SKY_BLUE}Transmission daemon${RESET}"
printf "\n%.0s" {1..1}

echo "${NOTE} By default, Transmission creates a separate user \"transmission\" for security measures. This script agrees with that conception."

# (from https://wiki.archlinux.org/title/Transmission#Web_interface)
shared_dir="/mnt/data/torrents"
echo "${INFO} Creating shared download dir for transmission and system users at $shared_dir"
sudo mkdir -p "$shared_dir"
sudo chown -R $(whoami):transmission "$shared_dir"
sudo chmod -R 775 "$shared_dir"

# Setting up daemon config
daemon_config="/var/lib/transmission/.config/transmission-daemon/settings.json"
if [ ! -f $daemon_config ]; then
  echo "${WARN} Configuration file at $daemon_config not found"
  echo "${MAGENTA}Awakening daemon so it generates a default configuration file..${RESET}"
sudo systemctl start transmission-daemon
sleep 1
transmission-remote --exit
fi

# Modify config to use the shared dir
echo "Updating the daemon configuration file at $daemon_config"
sudo sed -i "s|\(\"download-dir\": \)\"[^\"]*\"|\1\"$shared_dir\"|" $daemon_config
sudo sed -i "s|\(\"incomplete-dir\": \)\"[^\"]*\"|\1\"$shared_dir\"|" $daemon_config
sudo sed -i "s|\(\"incomplete-dir-enabled\": \)\"[^\"]*\"|\1\"true\"|" $daemon_config # BUG: fix boolean change

echo "${OK} Configuration updated."
echo "${INFO} Creating symlinked downloads directory."

DEFAULT_DOWNLOAD_PATH="$HOME/Downloads/Transmission-Downloads"

while true; do
  read -p "${CAT} Specify path for the downloads directory (leave empty for default location: \"$HOME/Downloads/Transmission-Downloads\"): " input_path
  symlink_dir="${input_path:-$DEFAULT_DOWNLOAD_PATH}"

  if mkdir -p "$symlink_dir" 2>/dev/null; then
    echo "Created directory \"$symlink_dir"
    break
  else
    echo "Failed to create directory \"$symlink_dir\". You might have wrong permissions."
  fi
done

# Create and sync the symlinked dir
ln -sfn $shared_dir $symlink_dir
echo "${INFO} Symlinked directory created"

printf "\n%.0s" {1..1}
read -p "${INFO} Daemon configuration finished. Do you want to start it now? [Y/n]" input
case "$input" in
  [nN])
  echo "${NOTE} Skipping daemon start. You can start it manually later with \"sudo systemctl start transmission-daemon\"";;
  *)
    echo "${INFO} Starting transmission daemon service"
    sudo systemctl start transmission-daemon
    if systemctl is-active --quiet transmission-daemon; then
      echo "${OK} Daemon active"
    fi
    ;;
esac
