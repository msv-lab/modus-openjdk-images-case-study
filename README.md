This repository hosts Modusfiles intended to generate OpenJDK images.

# OpenJDK versions

Below is a list that shows the ways in which an OpenJDK image can vary:
- MAJOR application version
  (Assume the most recent version of a given MAJOR application is used?)
- Runtime (jdk vs jre)
- Architecture (e.g. amd64)
- Base image variants (e.g. bullseye, buster, windows/nanoserver)
- GPG keys for signing binaries?

We can likely take combinations of these as goal tuples.
Although, note of course that not all combinations are valid, e.g. using a windows architecture is required
for a windows based variant.
