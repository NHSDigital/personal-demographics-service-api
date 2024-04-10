# Use the amazon corretto alpine image as the base - this gives us a lightweight image with Amazon's distribution of OpenJDK 17
FROM amazoncorretto:17-alpine-jdk
RUN apk add --no-cache git
RUN apk add --no-cache maven

LABEL version="0.0.1"

# We store our karate jarfile in a secret location, so we need to mount the secret to access it
WORKDIR /source
RUN --mount=type=secret,id=jarfile_url \
    wget $(cat /run/secrets/jarfile_url) -O /source/karate.jar

# Copy the source code to the container and start the sandbox
COPY ./ /app/
WORKDIR /app/src/test/java
CMD ["java", "-cp", "/source/karate.jar:.", "com.intuit.karate.Main", "-m", "mocks/sandbox/sandbox.js", "-p", "9090"]
EXPOSE 9090