#!/usr/bin/env bash

modus build ./openjdk-images-case-study -f <(cat ./openjdk-images-case-study/*.Modusfile) 'openjdk(A, B, C)' --json > build.json;
jq '.[] | [.digest, (.args | join("-"))] | join(" ")' build.json | xargs -I % sh -c 'docker tag %';
jq '.[].args | join("-")' build.json | xargs -I % sh -c "container-diff diff openjdk:% daemon://%" | sed -n 6p | awk '{print $2 - $1;}';
