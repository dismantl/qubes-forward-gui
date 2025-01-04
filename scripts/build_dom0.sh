#!/bin/bash
uid=$(id -u)
gid=$(id -g)
scripts_dir=$(dirname "$0")
project_name="qubes-forward-gui"

# clear build shit
echo "clearing cache"
sudo rm -rf out/ dist/ $project_name/ build/ *.spec src/__pycache__

# build the app
echo "start app building"
scripts/docker-run.sh

# create archive
cd "$project_dir"
echo "creating archive"
rm $project_name.zip &> /dev/null
sudo cp -r dist/main $project_name

sudo chown -R $uid:$gid "$project_name"
cp static/* "$project_name/"
zip "$project_name.zip" -r "$project_name"

echo "md5sum binary: $(md5sum $project_name/main)"
echo "md5sum archive: $(md5sum $project_name.zip)"
sudo rm -rf out/ dist/ $project_name/ build/ *.spec src/__pycache__
