# qubes-forward-gui
Qt GUI for simple port forwarding. Forked from https://github.com/r3t4k3r/qubes-forward-gui, which is no longer available.

# Limitations
- Only TCP rules supported
- Only temporary rules created

# Install
## just download and start using 
execute in App VM, e.g. `personal`:
```
wget -O /tmp/q.zip https://github.com/dismantl/qubes-forward-gui/releases/latest/download/qubes-forward-gui.zip
```
execute in `dom0`:
```
cd /tmp && qvm-run --pass-io personal 'cat /tmp/q.zip' > q.zip && unzip q.zip && cd qubes-forward-gui && ./install.sh
qubes-forward-gui # or just open using Applications menu
```

## building from source
execute in any qube:
```
git clone https://github.com/dismantl/qubes-forward-gui.git
cd qubes-forward-gui
scripts/build_dom0.sh
```
