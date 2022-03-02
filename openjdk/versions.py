#!/usr/bin/env python3

import json
import urllib.request, json
import csv
from typing import List
import os

def generate_tabular():
    cols = ['major_version', 'version', 'java_type', 'variant', 'amd64_url', 'arm64v8_url', 'source']
    tups = []

    url = "https://raw.githubusercontent.com/docker-library/openjdk/master/versions.json"
    with urllib.request.urlopen(url) as url_opened:
        decoded = url_opened.read().decode()

        with open("versions.json", "w") as w:
            w.write(decoded)

        data = json.loads(decoded)

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
            if "jdk" in data[major_version]:
                jdk_arch_binaries = {arch:data[major_version]["jdk"]["arches"][arch] for arch in data[major_version]["jdk"]["arches"]}

            # jre
            alpine_jre_arch_binaries = jre_arch_binaries = None
            if "alpine" in data[major_version] and "jre" in data[major_version]["alpine"]:
                alpine_version = data[major_version]["alpine"]["version"] # alpine has different version
                alpine_jre_arch_binaries = {arch:data[major_version]["alpine"]["jre"]["arches"][arch] for arch in data[major_version]["jre"]["arches"]}
            if "jre" in data[major_version]:
                jre_arch_binaries = {arch:data[major_version]["jre"]["arches"][arch] for arch in data[major_version]["jre"]["arches"]}

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

    seen_urls = set()
    for row in rows:
        if row[3].startswith("windows"):
            continue
        if row[2] == "jre" and row[3].startswith("oraclelinux"):
            continue

        tup = (row[4], row[5])
        if tup in seen_urls:
            continue
        seen_urls.add(tup)

        filename = f"binary_dockerfiles/{row[0]}-{row[2]}-{str(row[3].startswith('alpine')).lower()}.Dockerfile"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as out:
            out.write("FROM alpine:latest\n")
            out.write(f"RUN set -eux; \
arch=\"$(apk --print-arch)\"; \
case \"$arch\" in \
'x86_64') \
downloadUrl='{tup[0]}'; \
;; \
'aarch64') \
downloadUrl='{tup[1]}'; \
;; \
*) echo >&2 \"error: unsupported architecture: '$arch'\"; exit 1 ;; \
esac; \
wget -O openjdk.tgz \"$downloadUrl\";\n")
            out.write("RUN mkdir -p /opt/openjdk; \
tar --extract \
--file openjdk.tgz \
--directory \"/opt/openjdk\" \
--strip-components 1 \
--no-same-owner \
; \
rm openjdk.tgz*;\n")

if __name__ == "__main__":
    main()
