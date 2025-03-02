

## Installation

Have a good Java for Kafka

```
java --version
```

```
openjdk 21.0.5 2024-10-15 LTS
OpenJDK Runtime Environment Temurin-21.0.5+11 (build 21.0.5+11-LTS)
OpenJDK 64-Bit Server VM Temurin-21.0.5+11 (build 21.0.5+11-LTS, mixed mode, sharing)
```

A tool to help manage Java versions on your machine
https://sdkman.io/

A bit like nvm for Node 
https://github.com/nvm-sh/nvm

```
brew install kafka
```

```
brew services start zookeeper
brew services start kafka
```

```
brew services list
```

```
kafka         started burr ~/Library/LaunchAgents/homebrew.mxcl.kafka.plist
ollama        none
podman        none
postgresql@14 started burr ~/Library/LaunchAgents/homebrew.mxcl.postgresql@14.plist
rabbitmq      none
unbound       none
zookeeper     started burr ~/Library/LaunchAgents/homebrew.mxcl.zookeeper.plist
```

```
ps grep java
```

Get a list of topics

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --list 
```

Create a topic

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --partitions 1 --replication-factor 1 --topic test_topic 
```

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --partitions 1 --replication-factor 1 --topic review-gpt4o
```

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --list
```

```
test_topic
```

## kakfacat, kcat

Use Kafkacat/kcat to test some pub/sub

```
brew install kcat
```

Terminal 1: Consumer

```
kcat -C -b localhost:9092 -t test_topic
```

Terminal 2: Producer

```
echo "Your message here" | kcat -P -b localhost:9092 -t test_topic
```

Add a Terminal 3: Consumer

```
kcat -C -b localhost:9092 -t test_topic
```

All consumers see all the messages (its a Topic)

Add a consumer group so that only a single consumer gets a message

Cntrl-c the previously running consumers and restart with 

```
kcat -C -b localhost:9092  -G my_consumer_group test_topic
```

now publish a message

```
kcat -b localhost:9092 -t test_topic -P
```

```
1
2
3
4
```
Control-D

All messages go to the first consumer started, Control-C the first consumer and try to publish again

```
kcat -b localhost:9092 -t test_topic -P
```

```
5
6
7
8
```
Control-D

And now all messages flow to the second, still running, consumer


## Python


### Consumer

```
pip install kafka-python
```

```
python kafka-consumer.py
```

```
kcat -b localhost:9092 -t test_topic -P
```

### Producer

```
python kafka-producer.py
```

### Pydantic models/classes as Kafka messages

```
python kafka-producer-pydantic.py
```

```
python kafka-producer-consumer.py
```


### in-processor-out
An example of input topic, processing, output topic

set up the topics involved

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic input --partitions 1 --replication-factor 1
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic output --partitions 1 --replication-factor 1
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic review --partitions 1 --replication-factor 1
```

Add a message

```
python kafka-producer-pydantic.py
```

Process the message

```
python kafka-in-out.py
```

Terminal 2
see if it arrives in output

```
python kafka-consumer-pydantic.py
```

Terminal 3
or see if it arrives in review

```
kcat -C -b localhost:9092 -t review
```



## Backend: Python FastAPI

```
pip install fastapi uvicorn aiokafka sse-starlette websockets
```

```
uvicorn kafka-fastapi-consumer:app --reload
```

Now trigger the SSE which will start the consumer

```
curl -N http://localhost:8000/sse
```

Your messages should be logged AND thrown out to the curl client

You can open/see the swagger/OpenAPI docs via the browser

```
open http://localhost:8000/docs
```


## HTML/JS SSE Consumer

```
open sse-consumer.html
```

## streamlit consumer

```
pip install streamlit
pip install sseclient-py
pip install requests
pip install watchdog
```

Use the streamlit command to run the app

```
streamlit run streamlit-sse-receiver.py --server.headless true
```


## Clean up and recycle

Delete 
```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --delete --topic test_topic
```

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --list
```

and recreate
```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --create --topic test_topic --partitions 1 --replication-factor 1
```

```
/opt/homebrew/bin/kafka-topics --bootstrap-server localhost:9092 --list
```


 