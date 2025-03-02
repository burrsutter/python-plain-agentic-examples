/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --delete --topic input
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --delete --topic output
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --delete --topic review

/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic input --partitions 1 --replication-factor 1
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic output --partitions 1 --replication-factor 1
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic review --partitions 1 --replication-factor 1
