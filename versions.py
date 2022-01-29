#!/usr/bin/env python3

import json
import csv
from typing import List

def generate_tabular():
    # TODO: fetch from https://github.com/docker-library/openjdk/blob/master/versions.json
    filename = "versions.json"
    data = json.load(open(filename, 'r'))
    cols = ['major_version', 'version', 'java_type', 'variant', 'amd64_url', 'arm64v8_url', 'source']
    tups = []

    # e.g. .major_version.java_type.arches.arch.url
    for major_version in data:
        source = data[major_version]["source"]
        version = data[major_version]["version"]
        variants: List[str] = data[major_version]["variants"]

        # jdk
        alpine_version = alpine_jdk_arch_binaries = jdk_arch_binaries = None
        if "alpine" in data[major_version] and "jdk" in data[major_version]["alpine"]:
            alpine_version = data[major_version]["alpine"]["version"] # alpine has different version
            alpine_jdk_arch_binaries = {arch:data[major_version]["alpine"]["jdk"]["arches"][arch] for arch in data[major_version]["alpine"]["jdk"]["arches"]}
        elif "jdk" in data[major_version]:
            jdk_arch_binaries = {arch:data[major_version]["jdk"]["arches"][arch] for arch in data[major_version]["jdk"]["arches"]}

        # jre
        alpine_jre_arch_binaries = jre_arch_binaries = None
        if "alpine" in data[major_version] and "jre" in data[major_version]["alpine"]:
            alpine_version = data[major_version]["alpine"]["version"] # alpine has different version
            alpine_jre_arch_binaries = {arch:data[major_version]["alpine"]["jdk"]["arches"][arch] for arch in data[major_version]["jdk"]["arches"]}
        elif "jdk" in data[major_version]:
            jre_arch_binaries = {arch:data[major_version]["jdk"]["arches"][arch] for arch in data[major_version]["jdk"]["arches"]}

        # HACK: there's very likely a better way to define this logic
        for variant in variants:
            if variant.startswith("windows"):
                # No windows Arm support, see below link.
                # https://github.com/docker-library/bashbrew/blob/master/architecture/oci-platform.go
                windows_arch = "windows-amd64"
                if jdk_arch_binaries:
                    amd64 = jdk_arch_binaries[windows_arch]["url"] if (windows_arch in jdk_arch_binaries) else ""
                    arm64v8 = ""
                    tups.append((major_version, version, "jdk", variant, amd64, arm64v8, source))

                if jre_arch_binaries:
                    amd64 = jre_arch_binaries[windows_arch]["url"] if (windows_arch in jre_arch_binaries) else ""
                    arm64v8 = ""
                    tups.append((major_version, version, "jre", variant, amd64, arm64v8, source))
            elif variant.startswith("alpine"):
                if alpine_jdk_arch_binaries:
                    amd64 = alpine_jdk_arch_binaries["amd64"]["url"] if ("amd64" in alpine_jdk_arch_binaries) else ""
                    arm64v8 = alpine_jdk_arch_binaries["arm64v8"]["url"] if ("arm64v8" in alpine_jdk_arch_binaries) else ""
                    tups.append((major_version, alpine_version, "jdk", variant, amd64, arm64v8, source))

                if alpine_jre_arch_binaries:
                    amd64 = alpine_jre_arch_binaries["amd64"]["url"] if ("amd64" in alpine_jre_arch_binaries) else ""
                    arm64v8 = alpine_jre_arch_binaries["arm64v8"]["url"] if ("arm64v8" in alpine_jre_arch_binaries) else ""
                    tups.append((major_version, alpine_version, "jre", variant, amd64, arm64v8, source))
            else:
                if jdk_arch_binaries:
                    amd64 = jdk_arch_binaries["amd64"]["url"] if ("amd64" in jdk_arch_binaries) else ""
                    arm64v8 = jdk_arch_binaries["arm64v8"]["url"] if ("arm64v8" in jdk_arch_binaries) else ""
                    tups.append((major_version, version, "jdk", variant, amd64, arm64v8, source))

                if jre_arch_binaries:
                    amd64 = jre_arch_binaries["amd64"]["url"] if ("amd64" in jre_arch_binaries) else ""
                    arm64v8 = jre_arch_binaries["arm64v8"]["url"] if ("arm64v8" in jre_arch_binaries) else ""
                    tups.append((major_version, version, "jre", variant, amd64, arm64v8, source))
    return cols, tups

def main():
    cols, rows = generate_tabular()

    with open('versions.csv', 'w') as out:
        csv_out = csv.writer(out)
        csv_out.writerow(cols)
        csv_out.writerows(rows)

if __name__ == "__main__":
    main()
