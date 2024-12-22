#!/bin/bash
echo "start building pyui"
if [ -d 'src/pyui' ]; then
    echo "pyui folder found, building"
    rm -rf src/pyui/*
    pyuic6 ui -o src/pyui $@
    echo "finished"
else
    echo "pyui folder not found"
fi