#!/bin/bash

# Assumes modus is installed as well as openjdk and openjdk-images-case-study repos are present.

set -eux;

cd openjdk
git pull
cd ..
cd openjdk-images-case-study
./versions.py
cd openjdk
./versions.py
./update.sh
cd ../../

docker builder prune -a -f && docker image prune -a -f;
/usr/bin/time -o benchmarks/modus-time.log -a -p modus build ./openjdk-images-case-study 'openjdk(A, B, C)' -f <(cat ./openjdk-images-case-study/*.Modusfile) --image-export-concurrency=4;

docker builder prune -a -f && docker image prune -a -f;
fdfind Dockerfile$ ./openjdk | rg -v windows | /usr/bin/time -o benchmarks/official.log -a -p xargs -I % sh -c 'docker build . -f %';

docker builder prune -a -f && docker image prune -a -f;
fdfind Dockerfile$ ./openjdk | rg -v windows | /usr/bin/time -o benchmarks/official-parallel.log -a -p parallel --bar docker build . -f {};

docker builder prune -a -f && docker image prune -a -f;
cd ./openjdk-images-case-study/openjdk
/usr/bin/time -o ../../benchmarks/official-optimized.log -a -p ./build.sh
cd -
