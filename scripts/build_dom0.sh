#!/bin/bash
scripts_dir=$(dirname "$0")
project_dir="$scripts_dir/../"
archive_name="qubes-forward-gui"

# build the app
echo "start app building"
$scripts_dir/docker-run.sh

# clear build shit
echo "clearing cache"
#sudo rm -rf "$project_dir/out/" "$project_dir/build/" "$project_dir/runner.spec"

# create archive
cd "$project_dir"
echo "creating archive"
#rm $archive_name.zip
cp dist/runner $archive_name.bin
sudo rm -rf dist