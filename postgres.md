Going to use Tools and Postgres

## Installation and startup

```
brew install postgresql
```

```
brew services list
```

```
Name          Status User File
ollama        none
podman        none
postgresql@14 none   burr
rabbitmq      none
unbound       none
```

```
brew services start postgresql@14
```

## CLI psql

```
psql --version
```

```
psql (PostgreSQL) 14.16 (Homebrew)
```

```
psql -l
```

```
                         List of databases
   Name    | Owner | Encoding | Collate | Ctype | Access privileges
-----------+-------+----------+---------+-------+-------------------
 postgres  | burr  | UTF8     | C       | C     |
 template0 | burr  | UTF8     | C       | C     | =c/burr          +
           |       |          |         |       | burr=CTc/burr
 template1 | burr  | UTF8     | C       | C     | =c/burr          +
           |       |          |         |       | burr=CTc/burr
(3 rows)
```

```
psql
```

```
psql: error: connection to server on socket "/tmp/.s.PGSQL.5432" failed: FATAL:  database "burr" does not exist
```

```
createdb burr
```

Connect

```
psql -U burr -W
```

password is `admin` by default

```
\l
```

```
                         List of databases
   Name    | Owner | Encoding | Collate | Ctype | Access privileges
-----------+-------+----------+---------+-------+-------------------
 burr      | burr  | UTF8     | C       | C     |
 postgres  | burr  | UTF8     | C       | C     |
 template0 | burr  | UTF8     | C       | C     | =c/burr          +
           |       |          |         |       | burr=CTc/burr
 template1 | burr  | UTF8     | C       | C     | =c/burr          +
           |       |          |         |       | burr=CTc/burr
(4 rows)
```

```
CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'admin';
```

## Sample Databases

https://wiki.postgresql.org/wiki/Sample_Databases


### Netflix

```
curl -O https://raw.githubusercontent.com/neondatabase-labs/postgres-sample-dbs/main/netflix.sql
```

or perhaps
https://github.com/lerocha/netflixdb/releases


```
psql -U postgres -W
```

```
CREATE DATABASE netflix;
```

```
\c netflix
```

```
\i /Users/burr/my-projects/python-plain-agentic-examples/sample-dbs/netflix.sql
```

```
\d
```

```
Did not find any relations.
```

```
SET search_path TO schema_name, public;
```

```
\d
```

```
             List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+----------
 public | netflix_shows | table | postgres
(1 row)
```

```
select show_id,title from netflix_shows LIMIT 5;
```

```
 show_id |         title
---------+-----------------------
 s1      | Dick Johnson Is Dead
 s2      | Blood & Water
 s3      | Ganglands
 s4      | Jailbirds New Orleans
 s5      | Kota Factory
(5 rows)
```

### Northwind

```
psql -U burr -W
```

```
\l
```

```
                           List of databases
   Name    |  Owner   | Encoding | Collate | Ctype | Access privileges
-----------+----------+----------+---------+-------+-------------------
 burr      | burr     | UTF8     | C       | C     |
 netflix   | postgres | UTF8     | C       | C     |
 postgres  | burr     | UTF8     | C       | C     |
 template0 | burr     | UTF8     | C       | C     | =c/burr          +
           |          |          |         |       | burr=CTc/burr
 template1 | burr     | UTF8     | C       | C     | =c/burr          +
           |          |          |         |       | burr=CTc/burr
(5 rows)
```

```
CREATE DATABASE northwind;
```

```
\c northwind
```

```
\i /Users/burr/my-projects/python-plain-agentic-examples/sample-dbs/northwind.sql 
```

```
\d
```

```
                List of relations
 Schema |          Name          | Type  | Owner
--------+------------------------+-------+-------
 public | categories             | table | burr
 public | customer_customer_demo | table | burr
 public | customer_demographics  | table | burr
 public | customers              | table | burr
 public | employee_territories   | table | burr
 public | employees              | table | burr
 public | order_details          | table | burr
 public | orders                 | table | burr
 public | products               | table | burr
 public | region                 | table | burr
 public | shippers               | table | burr
 public | suppliers              | table | burr
 public | territories            | table | burr
 public | us_states              | table | burr
(14 rows)
```


```
select customer_id, company_name from customers limit 5;
```

```
 customer_id |            company_name
-------------+------------------------------------
 ALFKI       | Alfreds Futterkiste
 ANATR       | Ana Trujillo Emparedados y helados
 ANTON       | Antonio Moreno Taquería
 AROUT       | Around the Horn
 BERGS       | Berglunds snabbköp
(5 rows)
```

### Pagila

Sakila for Postgres - DVD Rentals

https://wiki.postgresql.org/wiki/Sample_Databases


```
psql -U burr -W
```

```
\l
```

```
                           List of databases
   Name    |  Owner   | Encoding | Collate | Ctype | Access privileges
-----------+----------+----------+---------+-------+-------------------
 burr      | burr     | UTF8     | C       | C     |
 netflix   | postgres | UTF8     | C       | C     |
 northwind | burr     | UTF8     | C       | C     |
 postgres  | burr     | UTF8     | C       | C     |
 template0 | burr     | UTF8     | C       | C     | =c/burr          +
           |          |          |         |       | burr=CTc/burr
 template1 | burr     | UTF8     | C       | C     | =c/burr          +
           |          |          |         |       | burr=CTc/burr
(6 rows)
```


```
CREATE DATABASE pagila;
```

```
\c pagila
```

```
\i /Users/burr/my-projects/python-plain-agentic-examples/sample-dbs/pagila-schema.sql 
```

```
SET search_path TO schema_name, public;
```

```
\d
```

```
                         List of relations
 Schema |            Name            |       Type        |  Owner
--------+----------------------------+-------------------+----------
 public | actor                      | table             | postgres
 public | actor_actor_id_seq         | sequence          | postgres
 public | actor_info                 | view              | postgres
 public | address                    | table             | postgres
 public | address_address_id_seq     | sequence          | postgres
 public | category                   | table             | postgres
 public | category_category_id_seq   | sequence          | postgres
 public | city                       | table             | postgres
 public | city_city_id_seq           | sequence          | postgres
 public | country                    | table             | postgres
 public | country_country_id_seq     | sequence          | postgres
 public | customer                   | table             | postgres
 public | customer_customer_id_seq   | sequence          | postgres
 public | customer_list              | view              | postgres
 public | film                       | table             | postgres
```


```
\i /Users/burr/my-projects/python-plain-agentic-examples/sample-dbs/pagila-insert-data.sql 
```

```
 select actor_id, first_name, last_name from actor limit 5;
```

```
 actor_id | first_name |  last_name
----------+------------+--------------
        1 | PENELOPE   | GUINESS
        2 | NICK       | WAHLBERG
        3 | ED         | CHASE
        4 | JENNIFER   | DAVIS
        5 | JOHNNY     | LOLLOBRIGIDA
(5 rows)
```

### IMDB

https://github.com/hakanersu/imdb-importer

or

https://dev.to/1mehal/script-to-import-imdb-database-into-postgresql-2lj3


### Chinook

Chinook uses table and column names like "Artist", this means you have also include double quotes with your SQL statements

```
curl -O https://raw.githubusercontent.com/neondatabase-labs/postgres-sample-dbs/refs/heads/main/chinook.sql
```

```
psql -U postgres -W
```

```
CREATE DATABASE chinook;
```

```
\c chinook
```

```
\i /Users/burr/my-projects/python-plain-agentic-examples/sample-dbs/chinook.sql
```

```
SET search_path TO schema_name, public;
```

```
\d
```

```
              List of relations
 Schema |     Name      | Type  |  Owner
--------+---------------+-------+----------
 public | Album         | table | postgres
 public | Artist        | table | postgres
 public | Customer      | table | postgres
 public | Employee      | table | postgres
 public | Genre         | table | postgres
 public | Invoice       | table | postgres
 public | InvoiceLine   | table | postgres
 public | MediaType     | table | postgres
 public | Playlist      | table | postgres
 public | PlaylistTrack | table | postgres
 public | Track         | table | postgres
(11 rows)
```

```
select "AlbumId", "Title" from "Album" limit 5;
```

```
  AlbumId |                                              Title
---------+-------------------------------------------------------------------------------------------------
       1 | For Those About To Rock We Salute You
       2 | Balls to the Wall
       3 | Restless and Wild
       4 | Let There Be Rock
       5 | Big Ones
```



### AdventureWorks

https://github.com/morenoh149/postgresDBSamples/tree/master/adventureworks

Adventureworks organizes tables into schemas

```
cd sample-dbs
```

```
psql -c "CREATE DATABASE \"Adventureworks\";"
```

```
psql -l
```

```
                             List of databases
      Name      |  Owner   | Encoding | Collate | Ctype | Access privileges
----------------+----------+----------+---------+-------+-------------------
 Adventureworks | burr     | UTF8     | C       | C     |
 burr           | burr     | UTF8     | C       | C     |
 netflix        | postgres | UTF8     | C       | C     |
 northwind      | burr     | UTF8     | C       | C     |
 pagila         | burr     | UTF8     | C       | C     |
 postgres       | burr     | UTF8     | C       | C     |
 template0      | burr     | UTF8     | C       | C     | =c/burr          +
                |          |          |         |       | burr=CTc/burr
 template1      | burr     | UTF8     | C       | C     | =c/burr          +
                |          |          |         |       | burr=CTc/burr
(8 rows)
```

```
psql -d Adventureworks < adventureworks.sql
```

```
 psql -U burr -W
```

```
\c Adventureworks
```

Schemas not "relations"

```
\dn
```

```
    List of schemas
      Name      | Owner
----------------+-------
 hr             | burr
 humanresources | burr
 pe             | burr
 person         | burr
 pr             | burr
 production     | burr
 pu             | burr
 public         | burr
 purchasing     | burr
 sa             | burr
 sales          | burr
(11 rows)
```

```
\dt sales.*
```

a bunch of tables

```
select * from "sales".customer limit 3;
```

```
 customerid | personid | storeid | territoryid |               rowguid                |      modifieddate
------------+----------+---------+-------------+--------------------------------------+-------------------------
          1 |          |     934 |           1 | 3f5ae95e-b87d-4aed-95b4-c3797afcb74f | 2014-09-12 11:15:07.263
          2 |          |    1028 |           1 | e552f657-a9af-4a7d-a645-c429d6e02491 | 2014-09-12 11:15:07.263
          3 |          |     642 |           4 | 130774b1-db21-4ef3-98c8-c104bcd6ed6d | 2014-09-12 11:15:07.263
(3 rows)
```

## Python

```
pip install psycopg2-binary
```

```
pip show psycopg2-binary
```

```
Name: psycopg2-binary
Version: 2.9.10
Summary: psycopg2 - Python-PostgreSQL Database Adapter
Home-page: https://psycopg.org/
Author: Federico Di Gregorio
Author-email: fog@initd.org
License: LGPL with exceptions
Location: /Users/burr/my-projects/python-plain-agentic-examples/venv/lib/python3.11/site-packages
Requires:
Required-by:
```

```
cd basics
```

```
python postgres-playground.py
```

```
List of databases:
- postgres
- burr
- netflix
- northwind
- pagila
List of tables in the database:
- categories
- customer_customer_demo
- customer_demographics
- customers
- employee_territories
- employees
- order_details
- orders
- products
- region
- shippers
- suppliers
- territories
- us_states
List of customers:
('ALFKI', 'Alfreds Futterkiste', 'Maria Anders')
('ANATR', 'Ana Trujillo Emparedados y helados', 'Ana Trujillo')
('ANTON', 'Antonio Moreno Taquería', 'Antonio Moreno')
('AROUT', 'Around the Horn', 'Thomas Hardy')
('BERGS', 'Berglunds snabbköp', 'Christina Berglund')
```


## GUI pgAdmin

https://www.pgadmin.org/download/

![pgAdmin4 1](/images/pgAdmin4-1.png)

![pgAdmin4 2](/images/pgAdmin4-2.png)


## Shutdown

```
brew services stop postgresql@14
```

```
brew services list
```

## Adding pgvector

```
brew install pgvector
```

Restart the overall service (unclear if this is required or just good form)

```
brew services restart postgresql
```


```
psql postgres
```

```
\l
```

### Create a database and table

```
CREATE DATABASE myvectordb;
```

```
\l
```

```
\c myvectordb
```

```
CREATE EXTENSION vector;
```

See if the vector extension is working

```
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    embedding vector(3)
);
```

### CRUD

```
INSERT INTO items (embedding) VALUES ('[0.1, 0.2, 0.3]');
```

```
SELECT * FROM items;
```

```
 id |   embedding
----+---------------
  1 | [0.1,0.2,0.3]
(1 row)
```

```
SELECT *
FROM items
ORDER BY embedding <-> '[0.2, 0.1, 0.3]'
LIMIT 5;
```

```
 id |   embedding
----+---------------
  1 | [0.1,0.2,0.3]
(1 row)
```

```
UPDATE items
SET embedding = '[0.4, 0.5, 0.6]'
WHERE id = 1;
```

```
SELECT * FROM items;
```

```
 id |   embedding
----+---------------
  1 | [0.4,0.5,0.6]
(1 row)
```

```
DELETE FROM items
WHERE id = 1;
```

```
 id | embedding
----+-----------
(0 rows)
```

### Indexing

```
CREATE INDEX ON items USING hnsw (embedding);
```

#### cosign similiarity <=>

```
SELECT *
FROM items
ORDER BY embedding <=> '[0.2, 0.1, 0.3]'
LIMIT 5;
```

#### inner product <#>

```
SELECT *
FROM items
ORDER BY embedding <#> '[0.2, 0.1, 0.3]'
LIMIT 5;
```

