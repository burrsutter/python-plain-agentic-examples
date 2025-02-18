
# RAG Examples with pgvector

See postgres.md for Postgres and **pgvector** installation

## Basic RAG

```
psql postgres
```

```
CREATE DATABASE rag_db;
\c rag_db
```

```
quit
```

```
pip install openai
pip install psycopg2-binary
pip install numpy
pip install scipy
pip install pgvector
pip install langchain_huggingface
```

```
cd rag
```

```
python 1-ingest.py
```

```
psql rag_db
```

```
\d
```

```
                List of relations
 Schema |       Name       |   Type   |  Owner
--------+------------------+----------+----------
 public | documents        | table    | postgres
 public | documents_id_seq | sequence | postgres
(2 rows)
```

```
select content from documents;
```

```
                                       content
-------------------------------------------------------------------------------------
 Albert Einstein: Developed the theory of relativity. Famous for E=mc².
 Marie Curie: Pioneered research on radioactivity. First woman to win a Nobel Prize.
 Isaac Newton: Formulated the laws of motion and universal gravitation.
 Charles Darwin: Developed the theory of evolution by natural selection.
(4 rows)
```

```
python 2-retrieve-newton.py
```

```
What is Newton known for? Newton is known for formulating the laws of motion and universal gravitation.
What did Stephen Hawking do? I don't know.
Database connection closed.
```

```
python 2-retrieve-curie.py
```

```
What is Curie known for? Marie Curie is known for pioneering research on radioactivity and being the first woman to win a Nobel Prize.
What did Burr Sutter do? I don't know.
Database connection closed.
```

## Directory Ingestion with LangChain

LangChain recommeneded by ChatGPT

Clean out previous ingestions

sql terminal

```
psql rag_db
```

```
drop table documents;
drop table documentsone;
drop table documentstwo;
```

another terminal
```
pip install textract-py3
pip install langchain
pip install sentence-transformers
```

```
python 1-ingest-directory-ada.py
```
note: this process takes a few minutes depending on your hardware

sql terminal

```
select count(*) from documentsone;
```

```
 count
-------
   895
```

```
select left(content,100) from documents order by id DESC LIMIT 1;
```

```
                            left
------------------------------------------------------------
 The Project Gutenberg eBook of Through the Looking-Glass\r+
     \r                                                    +
 This ebook is for the use of anyone
(1 row)
```

```
python 2-retrieve-directory-ada.py
```

### mpnet

```
python 1-ingest-directory-mpnet.py
```

```
python 2-retrieve-directory-mpnet.py
```


## ToDos

query = "what is the mad hatter's riddle" with smaller/larger chunk_size+chunk_overlap
with text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
and the relationship to select count(*) documentsone;

make it work with vLLM and ollama


This is a long text. It contains multiple sentences. Some sentences are about apples. Other sentences are about bananas.  We want to process this text in chunks.

if chunk_size = 20 and chunk_overlap = 5:

Chunk 1: "This is a long text."
Chunk 2: "long text. It contains"
Chunk 3: "It contains multiple"
Chunk 4: "multiple sentences. Some"
Chunk 5: "sentences. Some sentences"
Chunk 6: "sentences are about apples."
Chunk 7: "about apples. Other"
Chunk 8: "Other sentences are about"
Chunk 9: "are about bananas. We"
Chunk 10: "bananas. We want to"
Chunk 11: "want to process this text"
Chunk 12: "process this text in chunks."

The optimal values for chunk_size and chunk_overlap depend on:

LLM context window: chunk_size should be smaller than the LLM's context window.
Nature of the text: Highly structured text (e.g., code, tables) might need smaller chunk_size and lower chunk_overlap. More narrative text might benefit from larger chunk_size and higher chunk_overlap.
Performance requirements: Larger chunk_overlap increases processing but improves context. Balance this with your performance needs.
