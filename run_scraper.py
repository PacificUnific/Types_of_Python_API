# for scraping
import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
# for regular expr
import re
# for '--dry_run' run argument
import argparse
# for console conclusion
from prettytable import PrettyTable
# for DB conclusion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Data
# for config file
import yaml
from yaml import SafeLoader


# read config file
with open('config.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
# get from 'data' all params
# for scrapping
scraper = data['scraper']
URL = scraper['url']
CAPTION = scraper['caption']
KEY = scraper['key']
# for database
db = data['db']
IP = db['ip']
PORT = db['port']
USER = db['username']
PASS = db['password']
DB_NAME = db['db_name']


def run_params():
    """
    Addition run parameter, which named by 'KEY'

    :rtype: <class 'argparse.Namespace'>
    :return: namespace of run parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(f'--{KEY}', default=False,
                        type=lambda x: (str(x).capitalize() == 'True'),
                        help='gives a opportunity to choose, what we'
                             'should do with a data scrapped from table')

    return parser.parse_args()


def print_to_console(headers, rows):
    """
    Reflects scrapped table to console

    :type headers: list
    :param headers: table headers
    :type rows: list
    :param rows: all table rows beside of headers
    """
    table = PrettyTable(headers)
    table.align = 'l'

    for row in rows:
        # get str with separator '\n' from list
        row[3] = '\n'.join(row[3])
        table.add_row(row)

    table._max_width = dict(zip(headers, [25]*len(headers)))

    # print table with his title
    print(CAPTION.center(len(CAPTION) + 50))
    print(table)


def add_to_db(notes):
    """
    Addition all rows from table

    :type notes: list
    :param notes: rows from table
    """
    # connect to server PostgreSQL on localhost with psycopg2
    print('Connection to database...')
    engine = create_engine(f'postgresql+psycopg2://{USER}:{PASS}@{IP}:{PORT}/{DB_NAME}', echo=True)
    engine.connect()
    print('Connection was established')

    # take changes in 'collected_data'

    # open session
    session = sessionmaker(bind=engine)
    s = session()

    # delete all notes
    print('Deleting old notes...')
    s.query(Data).delete()
    print('Deleting was executed')

    # add new notes
    print('Addition new notes...')
    for note in notes:
        note[3] = '; '.join(note[3])
        s.add(Data(note))
    # commit all changes
    s.commit()
    print('Notes was added')

    # close connection
    print('Closing the connection...')
    s.close()
    engine.dispose()
    print('Connection was closed')


def scrapping() -> tuple:
    """
    Scraps Wikipedia article about Python and collect data from Python's types table

    :rtype: tuple
    :return: lists of headers and all rows from scrapped table
    """

    response = requests.get(URL, headers=Headers(os="mac", headers=True).generate())

    # if page doesn't work, stop program by created error
    assert response.status_code == 200, "Try later, now we can't get access to this page"

    soup = BeautifulSoup(response.text, 'html.parser')

    # find necessary table by caption
    captions = soup.find_all('caption')
    table = None

    for caption in captions:
        if caption.text.replace('\n', '') == CAPTION:
            table = caption.find_parent('table')

    # if we can't find necessary table, just stop program
    assert table is not None, "Necessary table doesn't exist"

    # get all rows in table
    rows = list(table.find_all('tr'))

    # headers
    headers = list(table.find_all('th'))
    if headers:
        for i, header in enumerate(headers):
            headers[i] = header.text.replace('\n', '')
        # remove headers from all rows
        rows.pop(0)

    # other rows
    # each column rewrite like str without formatting in each row
    # remark:
    #   syntax_examples is a list of them
    for i, row in enumerate(rows):

        columns = row.find_all('td')
        # type
        columns[0] = columns[0].find('code').text.replace('\n', '')
        # mutability
        columns[1] = columns[1].text.replace('\n', '')
        # description
        desc = columns[2].text.replace('\n', '')
        desc = re.sub(re.compile('\[[0-9]+]'), '', desc)
        columns[2] = desc
        # syntax_examples
        codes = columns[3].find_all('code')
        for j, code in enumerate(codes):
            codes[j] = code.text
        columns[3] = codes

        # rewrite current row
        rows[i] = columns

    return headers, rows


# get info after scrapping
headers, rows = scrapping()
# if parameter is in namespace,
# we print table to console,
# else add it to database
namespace = run_params()
if getattr(namespace, KEY):
    print_to_console(headers, rows)
else:
    add_to_db(rows)
