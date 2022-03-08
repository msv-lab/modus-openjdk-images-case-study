#!/bin/bash

set -eux;

echo Our average image efficiency:
modus build ./openjdk-images-case-study 'openjdk(A, B, C)' -f <(cat ./openjdk-images-case-study/*.Modusfile) --json | jq .[].digest | xargs -I % sh -c 'dive % --ci' | grep efficiency | awk '{print $2;}' | python3 -c 'import fileinput; xs = [float(i) for i in fileinput.input()]; print(sum(xs)/len(xs))';

echo Their average image efficiency:
modus build ./openjdk-images-case-study 'openjdk(A, B, C)' -f <(cat ./openjdk-images-case-study/*.Modusfile) --json | jq '.[].args | join("-")' | xargs -I % sh -c 'dive openjdk:% --ci' | grep efficiency | awk '{print $2;}' | python3 -c 'import fileinput; xs = [float(i) for i in fileinput.input()]; print(sum(xs)/len(xs))';
