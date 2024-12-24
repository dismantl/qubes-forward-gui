# qubes-forward-gui
Qt GUI for simple port forwarding

# Screenshoots
![image](https://github.com/user-attachments/assets/60725e10-f744-4a24-9934-53d99322f793)
![image](https://github.com/user-attachments/assets/16061cc6-b592-4401-a786-d9986ca4d3e3)
![image](https://github.com/user-attachments/assets/91a4860e-37f8-4b6a-b0fb-dc2f6017e336)


# Limitations
- Now only TCP rules supported
- Now only temporary rules could be created
- Unstable now, may contains some bugs/errors

# Install
## just download and start using 
execute in `personal`:
```
wget -O /tmp/q.zip https://github.com/r3t4k3r/qubes-forward-gui/releases/latest/download/qubes-forward-gui.zip
```
execute in `dom0`:
```
cd /tmp && qvm-run --pass-io personal 'cat /tmp/q.zip' > q.zip && unzip q.zip && cd qubes-forward-gui && ./install.sh
qubes-forward-gui # or just open using Applications menu
```

## building from source
execute in any qube:
```
git clone https://github.com/r3t4k3r/qubes-forward-gui.git
cd qubes-forward-gui
scripts/build_dom0.sh
```

Sometimes after building software could just don't work, how i understand that is a pyinstaller bug. In any problems use `-d` flag for enable debugging
