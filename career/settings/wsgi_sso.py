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



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings_base")

class LoggingMiddleware:
    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = True
        environ['wsgi.run_once'] = True

        request = WSGIRequest(environ)
        os.environ['KRB5CCNAME'] = request.META['KRB5CCNAME']
        os.environ['REMOTE_USER'] = request.META['REMOTE_USER'].split('@')[0]
        conf.settings.DATABASES['default'].update({'USER': os.environ['REMOTE_USER']})
        django.setup(set_prefix=False)
        self.__application = WSGIHandler()
        def _start_response(status, headers, *args):
            return start_response(status, headers, *args)

        return self.__application(environ, _start_response)

application = LoggingMiddleware(None)
