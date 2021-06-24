from sqlalchemy import create_engine
from models import Base

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# for config file
import yaml
from yaml import SafeLoader

# read config file
with open('config.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)

# get from 'data' params for database
db = data['db']
IP = db['ip']
PORT = db['port']
USER = db['username']
PASS = db['password']
DB_NAME = db['db_name']

# get connection with postgres
connection = psycopg2.connect(user=USER, password=PASS)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
# create DB
cursor = connection.cursor()
try:
    cursor.execute(f'create database {DB_NAME}')
    print('DB is created')
except psycopg2.errors.DuplicateDatabase:
    print('This database has already existed')
finally:
    # сlose connection
    cursor.close()
    connection.close()

# connect to server PostgreSQL on localhost with psycopg2
engine = create_engine(f'postgresql+psycopg2://{USER}:{PASS}@localhost/{DB_NAME}', echo=True)
engine.connect()

# create tables declared in 'models.py'
Base.metadata.create_all(engine)

# close connection
engine.dispose()
