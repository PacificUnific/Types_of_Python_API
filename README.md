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

There are two tables in database: 'users' and 'collected_data'. 

First table is used for to authorised user gets access to information. 
It has several fields: id, username, password and dates of creating 
of account and last request.

Second table is organized not more complicated than previous. 
It also has the next fields: id, name of type, mutability, description
and syntax examples. This table is used for to forming response for 
authorised used.


