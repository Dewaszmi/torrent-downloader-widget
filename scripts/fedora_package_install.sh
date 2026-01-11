#!/usr/bin/env bash

# Ensure colors are available
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RESET=$(tput sgr0)

is_installed_fedora() {
  local target="$1"

  # 1. Check if it is a literal package name
  if rpm -q "$target" &>/dev/null; then
    return 0
  fi

  # 2. Check if it is a binary provided by a package
  # We check the command path to see if RPM owns it
  if rpm -q --whatprovides "$target" &>/dev/null; then
    return 0
  fi

  # 3. Last ditch: check if it's a binary in the path (e.g. manually installed)
  if command -v "$target" &>/dev/null; then
    return 0
  fi

  return 1
}

rpm_install() {
  local packages=("$@")

  for pkg in "${packages[@]}"; do
    if is_installed_fedora "$pkg"; then
      echo "Found ${GREEN}$pkg${RESET} (installed), skipping."
    else
      echo "${YELLOW}$pkg${RESET} not found, attempting to install..."
      sudo dnf install "$pkg" -y
    fi
  done
}

echo "Checking Fedora dependencies..."
rpm_install "$@"
