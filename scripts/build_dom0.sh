#!/bin/bash
uid=$(id -u)
gid=$(id -g)
scripts_dir=$(dirname "$0")
project_dir="$scripts_dir/../"
archive_name="qubes-forward-gui"

# build the app
echo "start app building"
$scripts_dir/docker-run.sh

# clear build shit
echo "clearing cache"
sudo rm -rf "$project_dir/out/" "$project_dir/build/" "$project_dir/*.spec"

# create archive
cd "$project_dir"
echo "creating archive"
rm $archive_name.zip &> /dev/null
sudo cp -r dist/main $archive_name
sudo chown -R $uid:$gid $archive_name
zip $archive_name.zip -r $archive_name
sudo rm -rf dist/ $archive_name *.spec
