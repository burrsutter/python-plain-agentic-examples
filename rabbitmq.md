
https://www.rabbitmq.com/tutorials/tutorial-one-python

or just have a conversation with ChatGPT. It provides the minimal tutorial and provides numerous helpful code examples

## Install on Mac

```
brew install rabbitmq
```

## Startup

```
brew services start rabbitmq
```

```
brew services list
```

```
/opt/homebrew/sbin/rabbitmqctl enable_feature_flag all
```

```
curl -u guest:guest http://localhost:15672/api/healthchecks/node
```

```
# for macOS Intel
export PATH=$PATH:/usr/local/sbin
# for Apple Silicon
export PATH=$PATH:/opt/homebrew/sbin
```

### Pub and Sub (produce and consume)

```
pip install pika
```

Publish 3 messages

```
python rabbitmq-publisher.py
python rabbitmq-publisher.py
python rabbitmq-publisher.py
```

see the queues on the broker

```
curl -sS -u guest:guest http://localhost:15672/api/queues | jq '.[].name'
# or
curl -sS -u guest:guest http://localhost:15672/api/queues | jq '[.[].name]'
# or
curl -sS -u guest:guest http://localhost:15672/api/queues | jq '[.[].name | select(startswith("my_"))]'
```

Consume all messages and block, waiting for more messages

```
python rabbitmq-consumer.py
```

Check on the number of consumers

```
curl -sS -u guest:guest http://localhost:15672/api/queues/%2F/my_queue | jq '.consumers'
1
```

Stop the consumer then publish and peek (peek means see but not consume)

```
python rabbitmq-publisher.py
```

### Peek

```
python rabbitmq-peek-stats.py
```

### Priority

```
python rabbitmq-priority-queue.py
```

```
curl -sS -u guest:guest http://localhost:15672/api/queues | jq '.[].name'
```

```
"priority_queue"
```

```
curl -sS -u guest:guest http://localhost:15672/api/queues/%2F/priority_queue
```




## Shutdown, clean up

```
brew services stop rabbitmq
```

```
brew services list
```

```
Name          Status User File
ollama        none
postgresql@14 none   burr
rabbitmq      none
```

Does this clean out the underlying database/persistence? Seems to as upon next `start` I do not find the previously created queues

