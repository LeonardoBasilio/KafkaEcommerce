# Use a imagem Alpine como base
FROM alpine:3.14

# Atualize os repositórios e aplique atualizações no Alpine
RUN apk update && \
    apk upgrade --no-cache && \
    apk add bash && \
    apk add openjdk11

# Defina a variável de ambiente JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk

# Configure o diretório de trabalho para /app
WORKDIR /app

# Copie o Kafka para o diretório /app
COPY kafka_2.13-3.6.1 /app/kafka_2.13-3.6.1
