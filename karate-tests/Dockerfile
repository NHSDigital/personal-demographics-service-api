# Use the amazon corretto alpine image as the base - this gives us a lightweight image with Amazon's distribution of OpenJDK 17
FROM amazoncorretto:17-alpine-jdk
RUN apk add --no-cache git
RUN apk add --no-cache maven

LABEL version="0.0.1"

WORKDIR /source
RUN git clone https://github.com/NHSDigital/karate-jar 

COPY ./ /app/
WORKDIR /app/src/test/java
CMD ["java", "-cp", "/source/karate-jar/karate.jar:.", "com.intuit.karate.Main", "-m", "mocks/sandbox/sandbox.js", "-p", "9090"]
EXPOSE 9090