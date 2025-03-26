"""
WSGI config for LK project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

import django
from django import conf
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings_pam")

class LoggingMiddleware:
    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = True
        request = WSGIRequest(environ)
        passwd = r'%s' % request.META['HTTP_SESSION'].split('=')[2]
        passwd = passwd.replace('%21','!').replace('%40','@').replace('%23','#').replace('%24','$').replace('%25','%').replace('%5e','^').replace('%26','&')
        conf.settings.DATABASES['default'].update({'USER': request.META['REMOTE_USER']})
        conf.settings.DATABASES['default'].update({'PASSWORD': passwd})
        try:
            print("##############", request)
            print(request.META['REMOTE_USER'], os.getpid())
        except:
            pass
        django.setup(set_prefix=False)
        self.__application = WSGIHandler()
        def _start_response(status, headers, *args):
            return start_response(status, headers, *args)

        return self.__application(environ, _start_response)

application = LoggingMiddleware(None)
