# AI Agents in pure python

These examples from and inspired by Dave Ebbelaar's excellent video on how to build AI agents without a framework (in pure Python)

https://www.youtube.com/watch?v=bZzyPscbtI8

Dave was inspired by the following article from Anthropic

"Consistently, the most successful implementations weren't using complex frameworks or specialized libraries. Instead, they were building with simple, composable patterns."

https://www.anthropic.com/research/building-effective-agents


## Setup Python and openai API

```
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

```
pip install openai
pip install python-dotenv
pip install pydantic
pip install duckduckgo-search 
pip install requests
```


```
pip show openai
Name: openai
Version: 1.61.0
```

if on an older version, upgrade

```
pip install --upgrade openai
```

### OpenAI.com

Copy `.env-example` to `.env` 

or create env vars

```
export API_KEY=blah
export INFERENCE_SERVER_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o
```

These values can be overriden via `export API_KEY=something-else` to allow you hit multiple models from different terminal windows

### MaaS (self-service Model-as-a-Service)

This one is only available to Red Hatters.

https://maas.apps.prod.rhoai.rh-aiservices-bu.com/

Note: If there is question about the model name, use the `python 1-list-models.py` which only requires the URL and API_KEY.

If you receive `No Mapping Rule matched` it is likely that you forgot the `v1` at the end of the URL.


#### DeepSeek distilled qwen 14b

```
export API_KEY=blah
export INFERENCE_SERVER_URL=https://deepseek-r1-distill-qwen-14b-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1
export MODEL_NAME=deepseek-r1-distill-qwen-14b
```

#### Granite 8B

```
export API_KEY=blah
export INFERENCE_SERVER_URL=https://granite-3-8b-instruct-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1
export MODEL_NAME=granite-3-8b-instruct
```

Or for OTHER MaaS hosted mistral https://maas.apps.llmaas.llmaas.redhatworkshops.io/

```
export API_KEY=blah
export INFERENCE_SERVER_URL=https://mistral-7b-instruct-v0-3-maas-apicast-production.apps.llmaas.llmaas.redhatworkshops.io:443/v1
export MODEL_NAME=mistral-7b-instruct
```

#### Ollama

make sure to pick a tool enabled model

https://ollama.com/search?c=tools

Start the `ollama` server on localhost

```
ollama serve
```

```
curl http://localhost:11434
```

should respond with 

```
Ollama is running
```

Pull the desired model in advance.

https://ollama.com/library/qwen2.5-coder:14b-instruct-fp16

```
ollama pull qwen2.5-coder:14b-instruct-fp16
```

or

```
ollama pull granite3.1-dense:8b-instruct-fp16
```

or

```
ollama pull llama3.2:3b-instruct-fp16
```


Check your downloaded models by listing them 

```
ollama ls
```

No API_KEY needed for Ollama, just override the env var

```
export API_KEY=nothing
export INFERENCE_SERVER_URL=http://localhost:11434/v1
export MODEL_NAME=qwen2.5-coder:14b-instruct-fp16
```

or

```
export API_KEY=nothing
export INFERENCE_SERVER_URL=http://localhost:11434/v1
export MODEL_NAME=llama3.2:3b-instruct-fp16
```

You can also keep the models in memory with a -keepalive

```
ollama run llama3.2:3b-instruct-fp16 --keepalive 60m
```

To verify https://github.com/ollama/ollama/blob/main/docs/api.md#list-running-models

```
curl http://localhost:11434/api/ps
```

```
{"models":[{"name":"llama3.2:3b-instruct-fp16","model":"llama3.2:3b-instruct-fp16","size":8581748736,"digest":"195a8c01d91ec3cb1e0aad4624a51f2602c51fa7d96110f8ab5a20c84081804d","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama"],"parameter_size":"3.2B","quantization_level":"F16"},"expires_at":"2025-02-13T16:33:12.724036-05:00","size_vram":8581748736}]}%
```



## Test connectivity

```
cd basics
python 1-list-models.py
```

```
curl $INFERENCE_SERVER_URL/models \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json"
```

```
curl -sS $INFERENCE_SERVER_URL/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
     \"model\": \"$MODEL_NAME\",
     \"messages\": [{\"role\": \"user\", \"content\": \"Who is Burr Sutter?\"}],
     \"temperature\": 0.0
   }" | jq -r '.choices[0].message.content'
```

```
curl -sS $INFERENCE_SERVER_URL/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
     \"model\": \"$MODEL_NAME\",
     \"messages\": [{\"role\": \"user\", \"content\": \"How many seconds would it take for a leopard at full speed to run through Pont des Arts?\"}],
     \"temperature\": 0.0
   }" | jq -r '.choices[0].message.content'
```

## Chat Completions

https://platform.openai.com/docs/api-reference/chat

https://platform.openai.com/docs/guides/text-generation

```
python 2-chat-completions.py
```

## Structured Output

https://platform.openai.com/docs/guides/structured-outputs

https://docs.pydantic.dev/latest/


```
pip show pydantic
Name: pydantic
Version: 2.10.6
```

```
python 3-structured-output.py
```

## Tool calling

https://platform.openai.com/docs/guides/function-calling

and

https://ollama.com/blog/tool-support

https://ollama.com/search?c=tools

Where the model provides the "tool callback", you, the developer must provide the tool, describe the tool and invoke the tool.  The LLM simply suggests the when and with what parameters.

### Simple enterprisey example

```
python 4-tools-customer.py
```

### with Postgres

```
python 4-tools-customer-postgres-by-id.py
```

```
2025-02-15 16:08:15 - INFO - -------
2025-02-15 16:08:15 - INFO - <class '__main__.CustomerDetails'>
2025-02-15 16:08:15 - INFO - Customer ID: BERGS, Company Name: Berglunds snabbköp, Contact Name: Christina Berglund, Phone: 0921-12 34 65
2025-02-15 16:08:15 - INFO - -------
```

```
python 4-tools-customer-postgres-by-contact.py
```

```
2025-02-15 16:08:53 - INFO - -------
2025-02-15 16:08:53 - INFO - <class '__main__.CustomerList'>
2025-02-15 16:08:53 - INFO - Customer ID: BOTTM, Company Name: Bottom-Dollar Markets, Contact Name: Elizabeth Lincoln, Country: Canada, Phone: (604) 555-4729
2025-02-15 16:08:53 - INFO - Customer ID: CONSH, Company Name: Consolidated Holdings, Contact Name: Elizabeth Brown, Country: UK, Phone: (171) 555-2282
2025-02-15 16:08:53 - INFO - -------
```

### Make an external API a Tool


```
python 4-tools-weather.py
```

### DuckDuckGo 

Searching the internet to augment the knowledge the LLM.  


```
python 4-tools-duckduckgo.py
```

## Retrieval Augmentation

This is NOT an example with a vector database, embeddings and semantic search.  A more simplified example to augment the prompt, pushing the LLM to answer with your private data versus its default knowledge.  An attempt to reduce halluniciations.

```
python 5-basic-rag-like-artists.py
```

```
python 5-basic-rag-like-special-events.py
```

## Risk Detection

https://huggingface.co/ibm-granite/granite-guardian-3.0-8b

https://github.com/ibm-granite/granite-guardian/blob/main/cookbooks/granite-guardian-3.0/detailed_guide_ollama.ipynb

```
ollama pull granite3-guardian:8b-fp16
```

```
export MODEL_NAME=granite3-guardian:8b-fp16
export INFERENCE_SERVER_URL=http://localhost:11434/v1
```

Try some prompts 

```
python guardian-playground-risk.py
```

## workflows

combining the ideas from "basics" into chains & steps




## Logging

To enable logging output at the OpenAI level.  

```
export OPENAI_LOG=info
#  or
export OPENAI_LOG=debug
```

or simply use the logging framework 

``` 
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

```

## Questions, ToDos

If tool not invoked, how to retry, how many retries?
if tool is invoked with incorrect parameters, how to detect
If augmentations ignored
Better hallunication detection
Externalized prompts, prompts as code

MCP tool for SQL

Folder watcher for mock emails
Kafka listener/consumer for Debezium style support tickets
Router to appropriate in-box (Kafka Topic) 

routing example:
    technical support - technical support
    receipt/invoice - accounting/finance
    job/interview inquiry - human resources

screen via guardian
router, 3 processors

PII screening
https://github.com/Observicia/Observicia/blob/main/deploy/k8s/opa_policy_endpoint/pii/pii.py

Llama Stack examples
https://github.com/meta-llama/llama-stack-apps/blob/main/README.md

Anthropic Examples
https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents


Use Deepseek for planning, then faster tool callers like qwen for execution of the sub-tasks