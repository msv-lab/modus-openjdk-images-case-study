This repository hosts Modusfiles intended to generate OpenJDK images.

# Building

`modus build . 'openjdk(A, B, C, D, E, F)' -f linux.Modusfile` should build all available images.

# OpenJDK versions

Below is a list that shows the ways in which an OpenJDK image can vary:
- MAJOR application version
  (Assume the most recent version of a given MAJOR application is used?)
- Java type (jdk vs jre)
- Architecture (e.g. amd64, arm64, etc.). (Although this could be architectures, plural, in the future.)
- Base image variants (e.g. bullseye, buster, windows/nanoserver)
- GPG keys for verifying signed binaries?

We can likely take combinations of these as goal tuples.
Although, note of course that not all combinations are valid, e.g. using a windows architecture is required
for a windows based variant.

Also, note that the version + java type + arches may still not be enough to identify a binary to fetch,
since one needs to consider which libc was used, e.g. musl or glibc. (Maybe we should add this to
the variables?)

## Notes on Docker's Workflow

This attempts to be a tldr for https://github.com/docker-library/official-images,
specific to OpenJDK.
This may not be entirely accurate.

- `update.sh` calls `versions.sh` and `apply-templates.sh`.
- `versions.sh` updates `versions.json`
- `generate-stackbrew-library.sh` generates a summary of the available
images in a well-defined format (shared amongst similar repos).
- `apply-templates.sh` applies the linux/windows Dockerfile template using
jq/awk. This seems to use shared helper functions from bashbrew.
- The GH action jobs are generated using bashbrew, essentially based on
the different combinations of images allowed.

A good short example of an improvement over their template file is https://github.com/docker-library/openjdk/blob/f8d1fd911fdcad985d7a534e3470a9c54c87d45f/Dockerfile-linux.template#L36-L60.

## Note on Multi-Arch

Docker's OpenJDK image creation relies on determining the architecture at runtime.
Which allows them to isolate the logic that is specific to that architecture, and
also, I think, take advantage of `buildx`'s multi platform building (through QEMU).
