#!/usr/bin/env bash

sudo apt install pkgdiff -y;
modus build ./openjdk-images-case-study -f <(cat ./openjdk-images-case-study/*.Modusfile) 'openjdk(A, B, C)' --json > build.json;
jq '.[] | [.digest, (.args | join("-"))] | join(" ")' build.json | xargs -I % sh -c 'docker tag %';
jq '.[].args | join("-")' build.json | xargs -I % sh -c "docker create % | xargs docker export -o %_ours.tar; docker create openjdk:% | xargs docker export -o %_theirs.tar; echo %_theirs.tar %_ours.tar; timeout 1m pkgdiff %_theirs.tar %_ours.tar -quick; rm %_theirs.tar %_ours.tar; docker container prune -f";
