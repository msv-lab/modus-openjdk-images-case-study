This repository hosts Modusfiles intended to generate OpenJDK images.

# OpenJDK versions

Below is a list that shows the ways in which an OpenJDK image can vary:
- MAJOR application version
  (Assume the most recent version of a given MAJOR application is used?)
- Runtime (jdk vs jre)
- Architecture (e.g. amd64)
- Base image variants (e.g. bullseye, buster, windows/nanoserver)
- GPG keys for verifying signed binaries?

We can likely take combinations of these as goal tuples.
Although, note of course that not all combinations are valid, e.g. using a windows architecture is required
for a windows based variant.

Also, note that the version + runtime + arch may still not be enough to identify a binary to fetch,
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
