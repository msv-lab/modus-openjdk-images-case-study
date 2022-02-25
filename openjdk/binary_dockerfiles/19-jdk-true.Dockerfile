FROM alpine:latest
RUN set -eux; arch="$(apk --print-arch)"; case "$arch" in 'x86_64') downloadUrl='https://download.java.net/java/early_access/alpine/5/binaries/openjdk-19-ea+5_linux-x64-musl_bin.tar.gz'; ;; 'aarch64') downloadUrl=''; ;; *) echo >&2 "error: unsupported architecture: '$arch'"; exit 1 ;; esac; wget -O openjdk.tgz "$downloadUrl";
RUN mkdir -p /opt/openjdk; tar --extract --file openjdk.tgz --directory "/opt/openjdk" --strip-components 1 --no-same-owner ; rm openjdk.tgz*;
