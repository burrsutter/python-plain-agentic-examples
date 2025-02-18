See postgres.md for pgvector installation

## Basic

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

## Using files from local directory

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
python 1-ingest-directory-ada.py
```