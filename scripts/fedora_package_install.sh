#!/usr/bin/env bash

is_installed_rpm() {
  rpm -q "$1" &>/dev/null
}

rpm_install() {
  local packages=("$@")

  for pkg in "${packages[@]}"; do
    if is_installed_rpm "$pkg"; then
      echo "Found ${GREEN}$pkg$ {RESET}installation, skipping."
    else
      echo "${WARNING}$pkg installation not found, downloading.."
      sudo dnf install "$pkg" -y
    fi
  done
}

echo "Checking Fedora packages."
rpm_install "$@"
