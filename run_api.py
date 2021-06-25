# for application
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.httpclient
from tornado.options import define, options
import os
import json
import datetime
import hashlib

# for DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Data

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

# install of application's port
API_PORT = data['api']['port']

# creating of engine
engine = create_engine(f'postgresql+psycopg2://{USER}:{PASS}@{IP}:{PORT}/{DB_NAME}')


# connect to DB
def open_connection():
    """
    This function allows us to connect to database

    :rtype: <class 'sqlalchemy.orm.session.Session'>
    :return: session for sending queries to database
    """
    engine.connect()

    session = sessionmaker(bind=engine)()
    return session


def close_connection(session):
    """
    This function closes a connection to database

    :type session: <class 'sqlalchemy.orm.session.Session'>
    :param session: session, which used for executing of queries
    """
    engine.dispose()
    session.close()


class Application(tornado.web.Application):
    """
    Superclass, which is a subclass of Tornado class 'Application'
    """
    def __init__(self):
        """
        Here we define handlers, establish settings: set paths to
        templates and static files, also set security from XSRF
        """
        handlers = [
            (r'/api', MainHandler),
            (r'/api/reg', RegistrationHandler),
            (r'/api/login', AuthorizationHandler),
            (r'/api/logout', LogoutHandler),
            (r'/api/data', GettingDataHandler),
        ]
        settings = {
            'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'xsrf_cookies': True,
        }
        define('port', type=int, default=API_PORT)
        super(Application, self).__init__(handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    """
    Reflects main page
    """
    title = 'Main'
    address = 'layout.html'

    async def get(self):
        """
        Renders main page
        """
        await self.render(self.address, title=self.title, message='', login=self.get_cookie('user'))


class RegistrationHandler(tornado.web.RequestHandler):
    """
    Allows to register user
    """
    title = 'Registration'
    address = 'registration.html'

    async def get(self):
        """
        Renders registration page, if user isn't authorised
        """
        # if user is signed in, will returns 403 code
        if self.get_cookie('user'):
            self.send_error(403)
        else:
            await self.render(self.address, title=self.title, message='', login=self.get_cookie('user'))

    async def post(self):
        """
        Processes login and password
        Creates a new user
        """
        # if user is signed in, will returns 403 code
        if self.get_cookie('user'):
            self.send_error(403)
            return

        # get info from fields
        login = self.get_argument('login')
        password = self.get_argument('pass')
        rep_password = self.get_argument('rep_pass')

        # check of filling of all fields
        if login.strip() == '' or password.strip() == '' or rep_password.strip() == '':
            await self.render(self.address,
                              title=self.title,
                              message='All fields are necessary, please, fill them',
                              login=self.get_cookie('user'))

        # check of identity of passwords
        if password != rep_password:
            await self.render(self.address,
                              title=self.title,
                              message='Passwords do not match',
                              login=self.get_cookie('user'))

        # connect to DB
        s = open_connection()

        # check of existing of the same user's note
        if s.query(User).filter(User.login == login).count():
            await self.render(self.address,
                              title=self.title,
                              message='User exists with current login, come up with another name',
                              login=self.get_cookie('user'))

        # hashing of password
        password = hashlib.sha512(password.encode(encoding='utf-8')).hexdigest()

        # add new user's note to DB and redirect to main page
        user = [login, password]
        s.add(User(user))
        s.commit()
        close_connection(s)
        print('User was registered')
        self.set_cookie("user", login)
        self.redirect(r'/api')


class AuthorizationHandler(tornado.web.RequestHandler):
    """
    Gives an ability to user to sign in
    """
    title = 'Logging in'
    address = 'autorization.html'

    async def get(self):
        """
        Renders login page, if user isn't authorized
        """
        # if user is signed in, will returns 403 code
        if self.get_cookie('user'):
            self.send_error(403)
            return
        await self.render(self.address, title=self.title, message='', login=self.get_cookie('user'))
    
    async def post(self):
        """
        Processes login and password
        Allows user to sign in
        """
        # if user is signed in, will will returns 403 code
        if self.get_cookie('user'):
            self.send_error(403)
            return

        # get fields form autorization form
        login = self.get_argument('login')
        password = self.get_argument('pass')

        # check of filling of all fields
        if login.strip() == '' or password.strip() == '':
            await self.render(self.address,
                              title=self.title,
                              message='All fields are necessary, please, fill them',
                              login=self.get_cookie('user'))
            return

        # connect to DB
        s = open_connection()

        # hashing of password
        password = hashlib.sha512(password.encode(encoding='utf-8')).hexdigest()

        # if user exists then redirect him to main page
        if s.query(User).filter(User.login == login, User.password == password).count():
            self.set_cookie("user", login)
            self.redirect(r'/api')
            return
        else:
            await self.render(self.address,
                              title=self.title,
                              message='User does not exist with this password',
                              login=self.get_cookie('user'))


class LogoutHandler(tornado.web.RequestHandler):
    """
    Allows to log out
    """
    async def get(self):
        """
        Clears cookie (logs out), if user is authorised
        """
        # if user is signed in then log out
        if self.get_cookie('user'):
            self.clear_cookie('user')
        # finally redirection on login page
        self.redirect(r'/api/login')


class GettingDataHandler(tornado.web.RequestHandler):
    """
    Returns 'collected_data' notes from database
    """
    def prepare(self):
        """
        Preprocesses and saves notes as json in request
        """
        # take all notes in 'collected_data' from 'lst' by headers in 'col_titles'
        s = open_connection()
        lst = s.query(Data).filter().all()
        col_titles = Data.__table__.columns.keys()

        # forming answer to query in json format
        total = len(lst)
        data = [dict(zip(col_titles, [getattr(obj, title) for title in col_titles])) for obj in lst]
        ans = dict(data=data, total=total)
        # from 'dict' to 'str'
        json_string = json.dumps(ans)
        # forming request with encoding
        self.request.headers['Content-type'] = 'application/json'
        self.request.body = json_string.encode(encoding='utf-8')

    async def get(self):
        """
        Provides authorised user access to formed early data in request
        Writing json string on generated page
        """
        # get username from cookie
        login = self.get_cookie('user')

        # check autorization
        if not login:
            self.send_error(401)
            return

        # answer to request
        if self.request.headers['Content-Type'] == 'application/json':
            # update user's last request
            s = open_connection()
            s.query(User).filter(User.login == login).update({'last_request': datetime.datetime.utcnow()})
            s.commit()
            close_connection(s)
            # get from request body and convert from 'dict' to 'str'
            collected_data = json.loads(self.request.body.decode('utf-8'))
            json_string = json.dumps(collected_data, indent=4)
            # write response
            self.write(f'<pre style="word-wrap: break-word; white-space: pre-wrap;">{json_string}</pre>')


# run application
app = Application()
http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(options.port)
tornado.ioloop.IOLoop.current().start()
