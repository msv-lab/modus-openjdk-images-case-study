#!/usr/bin/env bash

modus build ./openjdk-images-case-study -f <(cat ./openjdk-images-case-study/*.Modusfile) 'openjdk(A, B, C)' --json > build.json;
jq '.[] | [.digest, (.args | join("-"))] | join(" ")' build.json | xargs -I % sh -c 'docker tag %';
jq '.[].args | join("-")' build.json | xargs -I % sh -c "echo -n '% '; docker image inspect % | jq .[].Size -j; echo -n ' '; docker image inspect openjdk:% | jq .[].Size" > compare.txt;
cat compare.txt | awk '{print $1, ($2 - $3 > 0 ? $2 - $3 : $3 - $2);}' | sort -n -k2;
