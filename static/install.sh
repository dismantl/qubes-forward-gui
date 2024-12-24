#!/bin/sh
echo "remove existing data"
sudo unlink /usr/bin/qubes-forward-gui &> /dev/null
sudo rm -rf /opt/qubes-forward-gui 2>/dev/null
sudo rm -rf /usr/share/applications/qubes-forward-gui.desktop 2>/dev/null

echo "creating directory"
sudo mkdir -p /opt/qubes-forward-gui

echo "copy files"
sudo cp -r . /opt/qubes-forward-gui
cd /opt/qubes-forward-gui

echo "creating .desktop application"
sudo mv qubes-forward-gui.desktop /usr/share/applications/

echo "adding qubes-forward-gui bianry to path"
sudo unlink /usr/bin/qubes-forward-gui &> /dev/null
sudo ln -s /opt/qubes-forward-gui/main /usr/bin/qubes-forward-gui