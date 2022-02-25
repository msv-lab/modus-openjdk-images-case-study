#!/usr/bin/env bash

#set -eux;

echo Build and tag the Dockerfiles that just fetch and extract the binaries.
fdfind Dockerfile$ ./binary_dockerfiles | sed "s/.Dockerfile//" | parallel --bar docker build -t {} . -f {}.Dockerfile

echo Extract the extracted binaries by starting a container.
# Could do this in parallel but I doubt much perf improvement.
mkdir ./binaries -p
for i in $(fdfind Dockerfile$ ./binary_dockerfiles | sed "s/.Dockerfile//")
do
    docker container create --name extract$$ $i
    docker container cp extract$$:/opt/openjdk/ ./binaries/$(basename $i)
    docker container rm -f extract$$
done

echo Finally, build the generated Dockerfiles, they should use the binaries dir, which should be present in their build context.
fdfind Dockerfile$ | rg -v '(binary_dockerfiles|windows)' | parallel --bar docker build . -f {}
