# Carjacker

## A TUI wrapper for Transmission / Jackett interfaces to allow for easy searching and managing of torrents in terminal.

### Description

Pretty much a terminal based version of BitTorrent with the search plugins for people enjoying TUIs.

The interface is split between two panes, one being a graphical wrapper for the Transmission torrent client, the other a simple search engine for the Jackett seeder API, allowing you to quickly search and manage torrents in a single terminal app.

### Installation

Clone the repository and run the install script:

```
git clone https://github.com/Dewaszmi/carjacker
cd carjacker
chmod +x install.sh
./install.sh
```

For RPM / Fedora based users the script automatically takes care of installing dependencies, other distributions might need to take care of installing them manually.

### Configuration

The Transmission config file is located at /var/lib/transmission/.config/transmission-daemon/settings.json.

The Jackett installation comes preconfigured with some of the popular indexers added, but users are welcome to review the configuration themselves at localhost:9117.