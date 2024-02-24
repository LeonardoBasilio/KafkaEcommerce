para executar o kafka
bin/kafka-server-start.sh config/server.properties

para acessar o terminal através do docker
docker exec -it kafka-kafka-broker-1-1 /bin/bash

para criar um tópico
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 replication-factor 1 --partitions 1 --topic NOME_DO_TOPICO

para listar os tópicos
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

parar gerar mensagem no tópico
bin/kafka-console-producer.sh --broker-list localhost:9092 --topic NOME_DO_TOPICO

para visualizar as mensagens no tópico desde do início
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic NOME_DO_TOPICO --from-beginning 
#kafka-console-consumer --bootstrap-server localhost:9092 --topic ECOMMERCE_NEW_ORDER --from-beginning

para visualizar algum arquivo dentro da imagem 
cat /etc/kafka/server.properties


para listar os arquivo que estão na imagem
docker exec -it kafka-kafka-broker-1-1 ls /etc/kafka/

para copiar um arquivo dentro da imagem docker para repositório local
docker cp kafka-kafka-broker-1-1:/etc/kafka/server.properties server.properties

para colar o arquivo do repositório local para o docker
docker cp server.properties kafka-kafka-broker-1-1:/etc/kafka/server.properties

para alterar o numero de partições
kafka-topics --bootstrap-server localhost:9092 --alter --topic ECOMMERCE_NEW_ORDER --partitions 3
