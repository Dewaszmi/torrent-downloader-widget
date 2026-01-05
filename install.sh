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

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

dependencies=(
  wget
  jq
  tar
  moreutils # for sponge
  transmission
  transmission-cli
  transmission-daemon
)

required_binaries=(
  wget
  jq
  tar
  sponge
  transmission-remote
  transmission-daemon
  pipx
)

# check for required executables
dependency_check() {
  local missing=()

  for binary in "${required_binaries[@]}"; do
    if ! command -v "$binary" &>/dev/null; then
      missing+=("$binary")
    fi
  done

  if [ ${#missing[@]} -eq 0 ]; then
    echo "${OK} All required executables found."
    return 0
  else
    echo "${ERROR} Missing executables:"
    for item in "${missing[@]}"; do
      echo "  - $item"
    done
    return 1
  fi
}

printf "\n%.0s" {1..2}
echo "Installing ${MAGENTA}Carjacker${RESET}."

# ============================
printf "\n%.0s" {1..2}
echo "${ORANGE}Act I: ${RESET}Dependency check"
printf "\n%.0s" {1..1}
# ============================

if cat /etc/*-release | grep "Fedora" &>/dev/null; then
  echo "${INFO}Found Fedora based distribution, running package check via dnf."
  sh scripts/fedora_package_install.sh
else
  echo "${INFO}You are running a Linux distribution other than Fedora, you might have to take care of installing dependencies yourself."
fi

if ! dependency_check; then
  echo "Aborting installation due to missing tools."
  echo "${ERROR} Please make sure the following packages are installed:"
  for pkg in "${dependencies[@]}"; do
    echo "  - $pkg"
  done

  exit 1
fi

echo "${OK} Installation completed."

# ============================
printf "\n%.0s" {1..2}
echo "${ORANGE}Act II: ${RESET}Configuring ${SKY_BLUE}Transmission daemon${RESET}."
printf "\n%.0s" {1..1}
# ============================

# (from https://wiki.archlinux.org/title/Transmission#Configuring_the_daemon)
echo "${NOTE} By default, Transmission creates a separate user \"transmission\" for security measures. This script follows that idea. To stop / start the daemon in the future, use standard systemctl utility."
echo "${WARN} Because of that however, the global configuration is going to be overwritten. If a non-default configuration has been detected, it will be saved to a .bak file in the same location."

# Setting up daemon configuration to point to the set download directory
echo "Configuring the Transmission daemon."

daemon_config="/var/lib/transmission/.config/transmission-daemon/settings.json"
if [ ! -f $daemon_config ]; then
  echo "${WARN} Configuration file at $daemon_config not found"
  echo "${MAGENTA}Awakening daemon so it generates a default configuration file..${RESET}"
  sudo systemctl start transmission-daemon
  transmission-remote --exit
else
  echo "${WARN} Found existing configuration file at $daemon_config."
  echo "The old configuration will be saved to $daemon_config.bak"
  sudo mv "$daemon_config" "$daemon_config.bak"
  sudo systemctl start transmission-daemon
  transmission-remote --exit
fi

shared_dir="/mnt/data/torrents"
echo "Creating shared download dir for transmission and current user at $shared_dir."
sudo mkdir -p "$shared_dir"
sudo chown -R $(whoami):transmission "$shared_dir"
sudo chmod -R 775 "$shared_dir"

# Modify config to use the shared dir
echo "Setting the download directory location in $daemon_config to $shared_dir."
sudo jq --arg dl "$shared_dir" \
  ' ."download-dir" = ($dl + "/complete") | 
  ."incomplete-dir" = ($dl + "/incomplete") | 
     ."incomplete-dir-enabled" = true ' \
  "$daemon_config" | sudo sponge "$daemon_config"

echo "${OK}Transmission configuration updated."

# Create a symlinked directory at $HOME/Downloads for convenience
echo "${INFO} Creating symlinked downloads directory."

DEFAULT_DOWNLOAD_PATH="$HOME/Downloads/Carjacker-Downloads"

while true; do
  read -p "${CAT} Specify path for the downloads directory (leave empty for default location: $DEFAULT_DOWNLOAD_PATH): " input_path
  symlink_dir="${input_path:-$DEFAULT_DOWNLOAD_PATH}"

  # Create and sync the symlinked dir
  if mkdir -p "$symlink_dir" 2>/dev/null; then
    ln -sfn "$shared_dir" "$symlink_dir"
    echo "${INFO} Created directory $symlink_dir symlinked to $shared_dir."
    break
  else
    echo "Failed to create directory \"$symlink_dir\". You might have wrong permissions."
  fi
done

printf "\n%.0s" {1..1}
read -p "${INFO} Transmission daemon configuration finished. Do you want to start it now? [Y/n]" input
case "$input" in
[nN])
  echo "${NOTE} Skipping daemon start. You can start it manually later with \"sudo systemctl start transmission-daemon\"."
  ;;
*)
  echo "Starting transmission daemon service."
  sudo systemctl start transmission-daemon
  if systemctl is-active --quiet transmission-daemon; then
    echo "Transmission active."
  fi
  ;;
esac

# ============================
printf "\n%.0s" {1..2}
echo "${ORANGE}Act III: ${RESET}Installing ${SKY_BLUE}Jackett service${RESET}."
printf "\n%.0s" {1..1}
# ============================

# Install Jackett as a systemd service, borrowed from https://github.com/Jackett/Jackett documentation
if ! systemctl list-unit-files jackett.service &>/dev/null; then
  cd /opt || exit
  f=Jackett.Binaries.LinuxAMDx64.tar.gz
  sudo wget -Nc https://github.com/Jackett/Jackett/releases/latest/download/"$f"
  sudo tar -xzf "$f"
  sudo rm -f "$f"
  cd Jackett* || exit
  sudo chown $(whoami):$(id -g) -R "/opt/Jackett"
  sudo ./install_service_systemd.sh
  systemctl status jackett.service
  cd - || exit
  echo -e "\nVisit http://127.0.0.1:9117"
else
  echo "${OK}${GREEN}Jackett ${RESET}service already installed, skipping."
fi

# ============================
printf "\n%.0s" {1..2}
echo "${ORANGE}Act IV: ${GREEN}Building package via ${SKY_BLUE}pipx${RESET}."
printf "\n%.0s" {1..1}
# ============================

cd "$PROJECT_ROOT" || {
  echo "${ERROR} Could not find project root."
  exit 1
}

if [ ! -f "pyproject.toml" ]; then
  echo "${ERROR} pyproject.toml not found in $(pwd). Are you in the right directory?"
  exit 1
fi

if pipx list | grep -q "carjacker"; then
  echo "${INFO} carjacker found, attempting upgrade..."
  # If upgrade fails due to the 'venv does not exist' error, reinstall
  if ! pipx upgrade . &>/dev/null; then
    echo "${NOTE} Upgrade failed (ghost installation detected). Performing clean reinstall..."
    pipx uninstall carjacker &>/dev/null
    pipx install .
  fi
else
  echo "${INFO} Installing carjacker for the first time..."
  pipx install .
fi

# ============================
printf "\n%.0s" {1..2}
echo "${ORANGE}Running final health check..."
printf "\n%.0s" {1..1}
# ============================

health_check() {
  local status=0

  if ! systemctl list-unit-files transmission-daemon.service &>/dev/null; then
    echo "${WARN}Transmission daemon service not found."
    status=1
  fi

  if ! systemctl list-unit-files jackett.service &>/dev/null; then
    echo "${WARN}Jackett service not found."
    status=1
  fi

  if [ ! -f "$daemon_config" ]; then
    echo "${WARN}Missing transmission config file at: $daemon_config."
    status=1
  fi

  if ! command -v carjacker &>/dev/null; then
    echo "${WARN}Missing carjacker binary in PATH."
    status=1
  fi

  return $status
}

if health_check; then
  echo "${OK}Installation finished succesfully."
else
  echo "${ERROR} System health check failed. Please fix the warnings above."
fi
