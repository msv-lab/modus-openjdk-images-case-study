#
# NOTE: THIS DOCKERFILE IS GENERATED VIA "apply-templates.sh"
#
# PLEASE DO NOT EDIT IT DIRECTLY.
#

FROM alpine:3.15

RUN apk add --no-cache java-cacerts

ENV JAVA_HOME /opt/openjdk-19
ENV PATH $JAVA_HOME/bin:$PATH

# https://jdk.java.net/
# >
# > Java Development Kit builds, from Oracle
# >
ENV JAVA_VERSION 19-ea+5
# "For Alpine Linux, builds are produced on a reduced schedule and may not be in sync with the other platforms."


COPY ./binaries/19-jdk-true $JAVA_HOME

RUN set -eux; \
	rm -rf "$JAVA_HOME/lib/security/cacerts"; \
# see "java-cacerts" package installed above (which maintains "/etc/ssl/certs/java/cacerts" for us)
	ln -sT /etc/ssl/certs/java/cacerts "$JAVA_HOME/lib/security/cacerts"; \
	\
# https://github.com/docker-library/openjdk/issues/212#issuecomment-420979840
# https://openjdk.java.net/jeps/341
	java -Xshare:dump; \
	\
# basic smoke test
	fileEncoding="$(echo 'System.out.println(System.getProperty("file.encoding"))' | jshell -s -)"; [ "$fileEncoding" = 'UTF-8' ]; rm -rf ~/.java; \
	javac --version; \
	java --version

# "jshell" is an interactive REPL for Java (see https://en.wikipedia.org/wiki/JShell)
CMD ["jshell"]
