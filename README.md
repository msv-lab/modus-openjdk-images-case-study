# Modus' OpenJDK Images 📦

This repository hosts Modusfile(s) intended to generate OpenJDK images.

---

# Building

`modus build . 'openjdk(A, B, C)' -f linux.Modusfile` should build all available images.

# Stats

## (Linux) All Major Versions, Java Types, and Variants

![image](https://user-images.githubusercontent.com/46009390/151715965-33c7e905-5e93-481b-ac26-bce68aa6c091.png)

As shown above, we are able to solve and build all 46 combinations of Linux-based OpenJDK images in under 15 minutes on a single machine.
This is from scratch, i.e. the time taken for SLD resolution + time taken for parallel build with an empty docker build cache.

## (Outdated) Single Variant and Java Type, Multiple Major Versions

TODO: update

An example of a typical use case, such as building all versions of OpenJDK from some base image:
![image](https://user-images.githubusercontent.com/46009390/151683270-eed95d58-8a97-4643-bc51-834b8f3e0ce8.png)

## Efficiency

We used [dive](https://github.com/wagoodman/dive) which provides an estimate of image efficiency[^1]. All the images we built scored over 95% image efficiency.

![image](https://user-images.githubusercontent.com/46009390/151718407-ba89e8d3-f2be-4ffe-a861-8cbb211395c0.png)

[^1]: Wasted space such as duplicating files across layers count as an 'inefficiency'.

## Compactness

TODO

# OpenJDK Configuration

Below is a list that shows the ways in which our OpenJDK configuration can 'vary', heavily inspired by the [official approach taken](https://github.com/docker-library/openjdk):
- Major application version
- Full version
- Java Type (JDK vs JRE)
- Base image variants (e.g. bullseye, buster, alpine3.15)
- AMD64 Binary URL
- ARM64 Binary URL
- Source

The variables exposed to a user are (a subset of the above):
- Major application version
- Java Type
- Variant

So a user may request a goal of `openjdk(A, "jdk", "alpine3.15")` to build all versions of JDK on Alpine.

# Disclaimer

The images we generate do not have identical layers. However, their filesystems and behaviour should be very close. Eventually their behaviour should be identical, but the goal is not (necessarily) to have identical *layers*.

In addition, we currently build more images than provided on Docker. So performance may be better than described.

## Notes on Docker's Official Workflow

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
