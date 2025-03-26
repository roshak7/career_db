#!/usr/bin/python3

# the code below is taken from and explained officially here:
# https://wsgi.readthedocs.io/en/latest/specifications/handling_post_forms.html
import cgi
import os
import pprint
import subprocess

import psycopg2
from django.core.handlers.wsgi import WSGIRequest
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings_pam")

def is_post_request(environ):
    if environ['REQUEST_METHOD'].upper() != 'POST':
        return False
    content_type = environ.get('CONTENT_TYPE', 'application/x-www-form-urlencoded')
    return (content_type.startswith('application/x-www-form-urlencoded' or content_type.startswith('multipart/form-data')))


def get_post_form(environ):
    assert is_post_request(environ)
    input = environ['wsgi.input']
    post_form = environ.get('wsgi.post_form')
    if (post_form is not None
            and post_form[0] is input):
        return post_form[2]
    # This must be done to avoid a bug in cgi.FieldStorage
    environ.setdefault('QUERY_STRING', '')
    fs = cgi.FieldStorage(fp=input,
                          environ=environ,
                          keep_blank_values=1)
    new_input = InputProcessed()
    post_form = (new_input, input, fs)
    environ['wsgi.post_form'] = post_form
    environ['wsgi.input'] = new_input
    return fs


class InputProcessed(object):
    def read(self, *args):
        raise EOFError('The wsgi.input stream has already been consumed')
    readline = readlines = __iter__ = read


def change_password(password=None, username=None, new_password=None):
    from django.conf import settings
    host = settings.DATABASES['default']['HOST']
    database = settings.DATABASES['default']['NAME']
    try:
        con = psycopg2.connect(host=host, database=database, user=username, password=password)
        cur = con.cursor()
        new_password = new_password.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$').replace(
            '%25',
            '%').replace(
            '%5e', '^').replace('%26', '&')
        sql = f"ALTER ROLE {username} WITH PASSWORD '{new_password}';"
        cur.execute(sql)
        con.commit()
        con.close()
    except Exception as err:
        # pass exception to function
        print(err)
        return False

    return True
# the basic and expected application function for wsgi
# get_post_form(environ) returns a FieldStorage object
# to access the values use the method .getvalue('the_key_name')
# this is explained officially here:
# https://docs.python.org/3/library/cgi.html
# if you don't know what are the keys, use .keys() method and loop through them
def application(environ, start_response):
    # password_old = get_post_form(environ).getvalue('password_old')
    password = get_post_form(environ).getvalue('password')
    old_password = get_post_form(environ).getvalue('old_password')
    request = WSGIRequest(environ)
    passwd = r'%s' % request.META['HTTP_SESSION'].split('=')[2]
    passwd = passwd.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$').replace('%25',
                                                                                                            '%').replace(
        '%5e', '^').replace('%26', '&')
    password = password.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$').replace('%25',
                                                                                                            '%').replace(
        '%5e', '^').replace('%26', '&')
    if old_password == passwd:
        user = environ.get('REMOTE_USER')

        try:
            output = subprocess.check_output(['/usr/bin/sudo', 'htpasswd', '-b', '/etc/apache2/passwd', user, password],
                                             timeout=5)
        except subprocess.CalledProcessError as exc:
            print("Status: FAIL {} {}".format(exc.returncode, "Ошибка при операции смены пароля."))
            pprint.pprint("Status: FAIL {} {}".format(exc.returncode, exc.output.decode()))
            start_response('301 Moved Permanently', [('Location', '/change/fail')])
            return ['fail'.encode()]
        else:
            if change_password(password=passwd, username=user, new_password=password) == True:
                start_response('301 Moved Permanently', [('Location', '/auth/index.html')])
                print("Status: SUCCESSFUL {}".format("Операция выполнена успешно."))
                return ['ok'.encode()]
            else:
                start_response('301 Moved Permanently', [('Location', '/change/fail')])
                return ['fail'.encode()]
    else:
        print("Status: FAIL Old Password is wrong!")
        start_response('301 Moved Permanently', [('Location', '/change/fail')])
        return ['fail'.encode()]


