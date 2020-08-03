#!/bin/bash

# check run environment
if [ "$1" == "sandbox" ]; then
  run_env="sandbox"
elif [ "$1" == "production" ]; then
  run_env="production"
else
  echo "Parameter One Should Be One Of: sandbox, production"
  exit
fi

# check package name
if [ "$2" == "reservations" ]; then
  lambda_name="reservations"
else
  echo "Parameter Two Should Be One Of: reservations"
  exit
fi

# cd to directory home
cd $3

# save home directory, source directory
home_dir=$(echo $PWD)
src_dir=$(echo $home_dir/source)

# make packages dir, cd into it
mkdir -p $home_dir/packages
cd packages
# make run env dir, cd into it
mkdir -p $home_dir/packages/$run_env
cd $home_dir/packages/$run_env
# make lambda specific dir, cd into it, save as variable
mkdir -p $home_dir/packages/$run_env/$lambda_name
cd $home_dir/packages/$run_env/$lambda_name
pack_dir=$(echo $PWD)

# get import list
imports=$(cat $src_dir/$lambda_name/requirements.txt)

# move to pack_dir, install requirements
cd $pack_dir
rm -r libs
mkdir -p libs
for import in $imports; do pip3 install --quiet --target $pack_dir/libs $import; done

# reservations gets aws-client, copy those files to libs folder
cp -r $src_dir/aws-clients $pack_dir/libs

# remove old lambda zip, cd into libs, zip together
rm lambda.zip
cd $pack_dir/libs
zip -r9q $pack_dir/lambda.zip .
cd $src_dir/$lambda_name
zip -ur9q $pack_dir/lambda.zip .

# output json to be used in other terraform modules
echo "{\"result\": \"true\", \"package_loc\": \"${pack_dir}\"}"



