from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

# superclass for creating of new models
Base = declarative_base()


class User(Base):
    """
    Create a new object of user's model

    :type user: list
    :param user: username and password
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    last_request = Column(DateTime)

    def __str__(self):
        """
        Outputs login field of this object

        :rtype: str
        :return: string of login current user (object)
        """
        return f'{self.login}'

    def __init__(self, user):
        self.login = user[0]
        self.password = user[1]


class Data(Base):
    """
    Creates a new object of model of Python's types

    :type row: list
    :param row: list of properties of note from 'collected_data'
    """
    __tablename__ = 'collected_data'

    id = Column(Integer, primary_key=True, nullable=False)
    type = Column(String, unique=True, nullable=False)
    mutability = Column(String, nullable=False)
    description = Column(String)
    syntax_examples = Column(String)

    def __str__(self):
        """
        Outputs type field of this object

        :rtype: str
        :return: string of name of type
        """
        return f'{self.type}'

    def __init__(self, row):
        self.type = row[0]
        self.mutability = row[1]
        self.description = row[2]
        self.syntax_examples = row[3]
