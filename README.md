# Modus' OpenJDK Images 📦

The [Docker Official Images](https://github.com/docker-library/official-images) project provides and maintains application runtimes packaged in images, such as [OpenJDK images](https://github.com/docker-library/openjdk), which we will refer to as _Docker's OpenJDK build system_ or DOBS.
Due to the limitations of Dockerfiles, DOBS relies on [Dockerfile templates](https://github.com/docker-library/openjdk/blob/c6190d5cbbefd5233c190561fda803f742ae8241/Dockerfile-linux.template), [bash scripts](https://github.com/docker-library/openjdk/blob/abebf9325fea4606b9759fb3b9257ea3eef40061/apply-templates.sh), as well as [jq and awk processing](https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk).
This serves as a method to conditionally execute instructions, or select between configuration strings. 
The reliance on _ad hoc_ solutions such as awk/jq templating causes maintainability problems. Firstly, developers must learn and be proficient in multiple languages and tooling to maintain the image build definitions and generation scripts. Secondly, these image build definitions are verbose.

[Modus](https://modus-continens.com) is a language for building OCI container images. Compared to Dockerfiles, Modus makes it easier to define complex, parameterized builds with negligible loss in efficiency w.r.t. build time or image sizes. 
Modus provides a cohesive system that replaces the need for Dockerfile templating. Another advantages of Modus is that using it requires you to think *explicitly* about the ways in which your builds can vary. In contrast, the official images *implicitly* define this through their [JSON versions file](https://github.com/docker-library/openjdk/blob/master/versions.json): it is not sufficient on its own to understand which configurations are valid, since one also needs to check the other scripts or template files. For example, one would need to [check their templating script](https://github.com/docker-library/openjdk/blob/ce82579fcff27d724a50ceaa4f1c140ac0102f39/apply-templates.sh#L47-L49) to realize that Oracle-based JRE images are unsupported.

## Code Size

A [single 267 line Modusfile](./linux.Modusfile) holds the conditional logic that defines all the varying image builds. In contrast, the templating approach requires a [332 line template file](https://github.com/docker-library/openjdk/blob/c6190d5cbbefd5233c190561fda803f742ae8241/Dockerfile-linux.template), a [77 line script](https://github.com/docker-library/openjdk/blob/abebf9325fea4606b9759fb3b9257ea3eef40061/apply-templates.sh) to apply the template, and a [140 line file](https://github.com/docker-library/bashbrew/blob/master/scripts/jq-template.awk) that defines some helper functions using awk and jq.

Below are statistics for (variations of) the `linux.Modusfile` according to `wc` applied to variations of the files:
|      Variation                               | Newlines | Words | Bytes |
|----------------------------------------------|---------:|------:|------:|
| Unedited                                     | 267      | 869   | 10389 |
| Comments/empty lines removed                 | 246      | 750   | 9607  |
| Comments/empty lines & select tokens removed | 244      | 695   | 7645  |

Below are the combined statistics for (variations of) the files needed for templating, as mentioned above:
|      Variation                               | Newlines | Words | Bytes |
|----------------------------------------------|---------:|------:|------:|
| Unedited                                     | 549      | 2209  | 16109 |
| Comments/empty lines removed                 | 441      | 1556  | 10626 |
| Comments/empty lines & select tokens removed | 403      | 1326  |  9642 |

## Build Time - AWS (c5.2xlarge)

Full details on the c5.2xlarge hardware are [here](https://aws.amazon.com/ec2/instance-types/c5/).

- We compared performance of the official Dockerfiles and our Modusfile. To provide a baseline for our performance tests, we built the official Dockerfiles sequentially using a shell script `time fdfind Dockerfile$ | rg -v windows | xargs -I % sh -c 'docker build . -f %'`.
- We built the Dockerfiles in parallel using GNU's `parallel` (to replicate Modus' approach of parallel builds) `time fdfind Dockerfile$ | rg -v windows | parallel --bar docker build . -f {}`.
- We executed Modus using the command `time modus build . 'openjdk(A, B, C)' -f <(cat *.Modusfile)` to build all available images. This builds the same 40 images[^image-count] that were built through the official approach.
All builds were executed with empty Docker build cache.

Modus performs better than the other approaches since DOBS' template processing took a significant fraction of the total time to build images.

[^image-count]: The number of images and the binaries themselves vary, so this is the number of images available at the time we conducted the benchmarks.

### OpenJDK optimizations without Modus

The official Dockerfiles do not take advantage of either multi-stage builds or the caching which would be easier to implement[^cache] with multi-stage builds.
Since these are the primary ways Modus improves on performance, we decided to extend the existing OpenJDK approach to implement these optimizations _without Modus_.

These hand written optimizations actually did not perform better than the naive parallel builds. 
This may be due to the non-trivial overhead of copying gigabytes of data which is a necessary step in this builder pattern. 
In addition, it is quite possible that most parallel orderings (GNU's `parallel` does not default to running *all* the builds at once) of image builds already avoid the duplicate fetching of binaries that we are
trying to optimize out. So the file copying that we introduce outweighs the benefits of avoiding some network fetches.

This does show that an even more complicated approach would be required for (consistently) better performance, motivating the use of a system like Modus.

[^cache]: Simply adding multi-stage builds does not give 'free' caching if one builds images in parallel.

### Summary

Applying the templates to generate the official OpenJDK Dockerfiles took **μ_t = 121.1s**, averaged over **10 runs**.

Here are the full results averaged over **10 runs** for each approach. The final column simply adds 121.1s where appropriate.
We've included the exporting time, which is a subset of the total build time using Modus, since this represents an operation
performed by Modus that could reduced in future versions.

| DOBS Variant        | μ (s) | μ + μ_t (s) |
|---------------------|-------|-------------|
| Sequential          | 516.3 | 637.4       |
| Parallel            | 119.8 | 240.9       |
| Manual Optimization | 276.7 | 397.8       |

| Modus               | μ (s) | μ + μ_t (s) |
|---------------------|-------|-------------|
| Total               | 143.1 | 143.1       |
| Exporting           | 18.0  | N/A         |

We used a local Docker registry that caches base images to avoid rate limiting. This leads to a minor speedup, consistent for any of the approaches (i.e. all approaches use these cached base images).

## Image Efficiency

We used [dive](https://github.com/wagoodman/dive) which provides an estimate of image efficiency. 
An example of an 'inefficiency' would be moving files across layers - this is a change that needs to be recorded as part of the layer, yet could be avoided by rewriting the Dockerfile.

| Approach | Average Efficiency |
|--|--:|
| Built with our Modusfiles | 98.9 |
| Official OpenJDK Images | 98.8 |

The official OpenJDK images also score highly on image efficiency (all above 95%), but at a cost to readability and separability.
Nearly [half of their Dockerfile](https://github.com/docker-library/openjdk/blob/ffcc4b9190be32ed7c4c92f6aa8fe2463da291d6/Dockerfile-linux.template#L187-L332) is a single `RUN` layer, to avoid the issue of modifications recorded in the layer diffs bloating the image size.

Modus provides a `merge` operator to solve this issue, which helped us achieve high image efficiency scores. `merge` is an operator that will merge the underlying commands of an expression into one `RUN` layer.

https://github.com/modus-continens/openjdk-images-case-study/blob/5c9783c4cc9d37ab56da529434e876de1f422219/linux.Modusfile#L267-L271

In this case, if we remove the `merge`, the image efficiency drops to about 75%. One operation that contributes to the inefficiency is updating `cacerts` in a separate `RUN` layer, and there may be other similar operations performed within the body of this `merge` that create a new layer with _avoidable_ diffs.

This demonstrates that `merge` facilitates the best of both worlds: the readability of separating out sections of code without the inefficiency of more layers recording more diffs.

# Querying our Build System

The variables exposed to a user are (a subset of the parameters that can vary for a build):
- Major application version
- Java Type
- Variant

So a user may request a goal of `openjdk(A, "jdk", "alpine3.15")` to build all versions of JDK on Alpine.

Below is a complete list that shows the ways in which our OpenJDK configuration can vary, heavily inspired by the [official approach taken](https://github.com/docker-library/openjdk):
- Major application version
- Full version
- Java Type (JDK vs JRE)
- Base image variants (e.g. bullseye, buster, alpine3.15)
- AMD64 Binary URL
- ARM64 Binary URL
- Source

## Diagram of Docker's OpenJDK Build System (DOBS)

![image](https://user-images.githubusercontent.com/46009390/161997869-e541108b-bc21-446b-8450-36475d05b88b.png)
