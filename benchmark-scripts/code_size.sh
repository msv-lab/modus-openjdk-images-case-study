#!/usr/bin/env bash

# Use this script like `./code_size.sh file1 file2 ... > output.txt`

set -eu;

function estimate()
{
    echo Estimating code size of $1
    cat $1 | wc

    # without comments and empty lines:
    sed 's/#.*//' $1 \
        | sed '/^\s*$/d' \
        | wc

    # Without the following tokens:
    # - '\' at the end of a line.
    # - '{{' (removed only if it's a template file)
    # - '}}' or '-}}' (removed only if it's a template file)
    # - '[ \t]+' replaced with a single space
    # - trailing whitespaces
    # as well as all the comments and empty lines removed.

    case "$1" in
        *template*)
            sed 's/#.*//' $1 \
                | sed 's/\\$//' \
                | sed 's/{{//g' \
                | sed 's/-\?}}//g' \
                | sed 's/[ \t]\+/ /g' \
                | sed 's/\s\+$//g' \
                | sed '/^\s*$/d' \
                | wc
            ;;
        *)
            sed 's/#.*//' $1 \
                | sed 's/\\$//g' \
                | sed 's/[ \t]\+/ /g' \
                | sed 's/\s\+$//g' \
                | sed '/^\s*$/d' \
                | wc
            ;;
    esac
}

for arg in $@
do
    estimate $arg
done
