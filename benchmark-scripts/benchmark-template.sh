#!/bin/bash

set -eux;

cd openjdk
/usr/bin/time -o ../benchmarks/template.log -a -p ./apply-templates.sh
