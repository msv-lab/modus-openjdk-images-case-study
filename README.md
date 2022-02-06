# Modus' OpenJDK Images 📦

The [Docker Official Images](https://github.com/docker-library/official-images) project provides and maintains application runtimes packaged in images, such as [OpenJDK images](https://github.com/docker-library/openjdk). Because Dockerfiles are not sufficently expressive, OpenJDK image build relies on [Dockerfile templates](https://github.com/docker-library/openjdk/blob/c6190d5cbbefd5233c190561fda803f742ae8241/Dockerfile-linux.template), [bash scripts](https://github.com/docker-library/openjdk/blob/abebf9325fea4606b9759fb3b9257ea3eef40061/apply-templates.sh), as well as [jq and awk processing](https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk). Often, this serves as a method to conditionally execute instruction, or select between configuration strings. The templated Dockerfile approach has several shortcomings: it requires developing and maintaining ad-hoc, complicated and error-prone string processing scripts, and make parallelisation less efficient.

[Modus](https://modus-continens.com) is a language for building OCI container images. Compared to Dockerfiles, Modus makes it easier to define complex, parameterized builds with zero loss in efficiency w.r.t. build time or image sizes. Furthermore, Modus can makes image creation faster via more effective parallelisation. Modus provides a cohesive system that replaces the need for Dockerfile templating, and most of the surrounding ad-hoc scripts. Another advantages of Modus is that using it requires you to think *explicitly* about the ways in which your builds can vary. In contrast, the official images *implicitly* define this through their [JSON versions file](https://github.com/docker-library/openjdk/blob/master/versions.json): it is not sufficient on its own to understand which configurations are valid, since one also needs to check the other scripts or template files. For example, one would need to read their [templating script](https://github.com/docker-library/openjdk/blob/master/apply-templates.sh) to realize that Windows variants are handled differently.

## Code Size

A [single 315 line Modusfile](./linux.Modusfile) holds the conditional logic that defines all the varying image builds. In contrast, the templating approach requires a [332 line template file](https://github.com/docker-library/openjdk/blob/c6190d5cbbefd5233c190561fda803f742ae8241/Dockerfile-linux.template), a [77 line script](https://github.com/docker-library/openjdk/blob/abebf9325fea4606b9759fb3b9257ea3eef40061/apply-templates.sh) to apply the template, and a [140 line file](https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk) that defines some helper functions using awk and jq, totally 549 LoC.

## Build Time

We compared performance of the official Dockerfiles and our Modusfile. To provide a baseline for our performance tests, we built the official Dockerfiles sequentially using a shell script `time fdfind Dockerfile$ | rg -v windows | xargs -I % sh -c 'docker build . -f %'`.
![image](https://user-images.githubusercontent.com/46009390/152654516-7e6583ca-c52e-42f0-bad9-c89db768b2be.png)

We executed Modus using the command `modus build . 'openjdk(A, B, C)' -f <(cat *.Modusfile)` to build all available images. 

![image](https://user-images.githubusercontent.com/46009390/152651786-853f2f4b-bbc6-4c8e-86cf-23cc3a9b62d9.png)

The experiments were executed [Intel(R) Core(TM) i5-10400F CPU @ 2.90GHz](https://www.intel.co.uk/content/www/uk/en/products/sku/199278/intel-core-i510400f-processor-12m-cache-up-to-4-30-ghz/specifications.html) with 6 total cores, and with 8GiB of RAM. All builds were executed with empty Docker build cache.

The baseline, building images sequentially from the official Dockerfiles, took __16:46__ minutes to build 42 images. Our approach, using Modus, took __13:34__ minutes to build the same 42 images. The performance improvements from using Modus is due to the parallel build performed by our front-end to BuildKit.

## Building Subset of Images

An example of a typical use case, such as building all versions of JDK on a particular base image (slim-bullseye):
![image](https://user-images.githubusercontent.com/46009390/152662841-8d266c69-96a7-42d7-b399-386b83de5668.png)

We're able to build 5 versions in 1:40 minutes.

## Image Efficiency

We used [dive](https://github.com/wagoodman/dive) which provides an estimate of image efficiency. Wasted space such as duplicating files across layers count as an 'inefficiency'. All the images we built scored over 95% image efficiency.

![image](https://user-images.githubusercontent.com/46009390/152662059-67ecc65e-6b41-4dc8-b18a-082e98597bd5.png)

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
