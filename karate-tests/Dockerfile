# Use the amazon corretto alpine image as the base - this gives us a lightweight image with Amazon's distribution of OpenJDK 17
FROM amazoncorretto:17-alpine-jdk
RUN apk add --no-cache git
RUN apk add --no-cache maven

# FROM maven:3-amazoncorretto-17
# RUN yum install -y git

# FROM mcr.microsoft.com/openjdk/jdk:17-ubuntu
# RUN apt-get update && apt-get install -y git maven
# RUN apt-get install -y git

LABEL version="0.0.1"

# option 1 - build a jarfile from a given commit - we run into the slf4j logging error
# Exception in thread "main" java.lang.NoClassDefFoundError: org/slf4j/LoggerFactory
#         at com.intuit.karate.FileUtils.<clinit>(FileUtils.java:50)
#         at com.intuit.karate.Main.main(Main.java:233)
# Caused by: java.lang.ClassNotFoundException: org.slf4j.LoggerFactory
#         at java.base/jdk.internal.loader.BuiltinClassLoader.loadClass(BuiltinClassLoader.java:641)
#         at java.base/jdk.internal.loader.ClassLoaders$AppClassLoader.loadClass(ClassLoaders.java:188)
#         at java.base/java.lang.ClassLoader.loadClass(ClassLoader.java:525)
#         ... 2 more
# This error happens with different base images:
# - amazoncorretto:17-alpine-jdk
# - maven:3-amazoncorretto-17
# - mcr.microsoft.com/openjdk/jdk:17-ubuntu
#
# We build the Karate jarfile from source as explained in https://github.com/karatelabs/karate/wiki/Developer-Guide
# Omit building the modules that aren't needed for running the sandbox
# RUN git clone https://github.com/karatelabs/karate.git /source/karate

# WORKDIR /source/karate
# RUN git checkout c0597e5b7fcd61be47f916854e8473da11b37956
# RUN mvn clean install -P pre-release -pl -karate-robot,-karate-playwright,-karate-e2e-tests

# WORKDIR /source/karate/karate-core
# RUN mvn package -P fatjar

# RUN cp /source/karate/karate-core/target/karate-core-1.6.0-SNAPSHOT.jar /source/karate.jar

# option 2 - download a jarfile from karatelabs. This isn't the version we need - can't connect to 127.0.0.1:9000 from outside the container
#
# WORKDIR /source/karate
# RUN wget https://github.com/karatelabs/karate/releases/download/v1.5.0.RC3/karate-1.5.0.RC3.jar -O /source/karate.jar


# option 3 - use the latest jarfile I've built on my own machine that works

COPY ./karate-1.6.0-SNAPSHOT.jar /source/karate.jar


# Copy the source code to the container and start the sandbox
COPY ./ /app/
WORKDIR /app/src/test/java
CMD ["java", "-cp", "/source/karate.jar", "com.intuit.karate.Main", "-m", "mocks/sandbox/sandbox.js", "-p", "9000"]