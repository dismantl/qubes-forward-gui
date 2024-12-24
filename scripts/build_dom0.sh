#!/bin/bash
uid=$(id -u)
gid=$(id -g)
scripts_dir=$(dirname "$0")
archive_name="qubes-forward-gui"

# clear build shit
echo "clearing cache"
sudo rm -rf out/ build/ *.spec src/__pycache__

# build the app
echo "start app building"
scripts/docker-run.sh

# create archive
cd "$project_dir"
echo "creating archive"
rm $archive_name.zip &> /dev/null
sudo cp -r dist/main $archive_name

sudo chown -R $uid:$gid "$archive_name"
cp static/* "$archive_name/"
zip "$archive_name.zip" -r "$archive_name"

echo "md5sum binary: $(md5sum $archive_name/main)"
echo "md5sum archive: $(md5sum $archive_name.zip)"
sudo rm -rf dist/ "$archive_name/" *.spec src/__pycache__
