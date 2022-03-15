#!/usr/bin/env bash

set -eu;

./code_size.sh ./openjdk-images/linux.Modusfile \
    jq-template.awk openjdk/Dockerfile-linux.template openjdk/apply-templates.sh;
