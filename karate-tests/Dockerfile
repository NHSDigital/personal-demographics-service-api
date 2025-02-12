FROM amazoncorretto:17-alpine-jdk
RUN apk add --no-cache git

LABEL version="0.0.1"

WORKDIR /source
RUN git clone https://github.com/NHSDigital/karate-jar 

COPY ./ /app/
WORKDIR /app/src/test/java
CMD ["java", "-cp", "/source/karate-jar/karate.jar:.", "com.intuit.karate.Main", "-m", "mocks/sandbox/sandbox.js", "-p", "9000"]
EXPOSE 9000