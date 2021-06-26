# Python's Types API

## Project Description

The main idea of this project is development of API allowed user
to get access to information about Python's types in detail.

Itself application was written with *Python 3.9.0*. Also here was used
libraries like *Tornado 6.1* for creating a web-application, 
*SQLAlchemy 1.4.18* for work with database written on 
[*PostgreSQL 13*](https://www.postgresql.org/download/ 
"Download PostgreSQL") and [*Swagger 3.0.3*](https://editor.swagger.io/
"Swagger specification editor") for creating of specification.

Info was token from Wikipedia article, and consideration of types
contents in table on this page. So to get it, uses libraries:
*Requests 2.25.1* for content's extract of current page and 
*BeautifulSoup 4.9.3* for scrapping information.

Libraries installation with pip.

```
pip install tornado
pip install sqlalchemy

pip install requests
pip install beautifulsoup4
```

There are two tables in database: '**users**' and '**collected_data**'. 

First table is used for to authorised user gets access to information. 
It has several fields: id, username, password and dates of creating 
of account and last request.

Second table is organized not more complicated than previous. 
It also has the next fields: id, name of type, mutability, description
and syntax examples. This table is used for to forming response for 
authorised used.

Itself web-application locates on **localhost:1235** (you can change 
port, as other settings, in config file '**config.yaml**'). 
If you add to address '**/api**', you will be redirected to main page. 
From it you can go to pages to register, authorise, log out and get 
info about Python's types.

Also it was written few handlers for work with users:
+ **/api/reg** - registration;
+ **/api/login** - sign in;
+ **/api/logout** - sign out.

If user is authorised, he can send request to '**/api/data**' and 
get response from it in format *'application/json'*.

Apply to '**swagger.json**' to know about work of all API-methods 
more detailed.

## Start-up Instruction

The steps, described below, need to execute, if you run application 
for the first time. You need to run '**db_init.py**' to initialize 
database. It creates a database and two tables, which have already 
been written early. After it, necessary is a execution of 
'**run_scraper.py**'. This script has run parameter ('*--dry_run*' 
by default), which can accept **True** or **False**. In first case 
program shows a table in console, else updates notes in database, 
in other words, deletes old in database and adds new, has just 
been scrapped, to it. If 'collected_data' is empty, '--dry_run False'
just creates notes in it. 

In common way, you just launch '**run_api**' and use this API.    