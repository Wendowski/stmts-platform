"""Development-only WSGI server; intentionally no DB migration check for read-only fixtures."""
import os
from wsgiref.simple_server import make_server
os.environ['STMTS_DEVELOPMENT']='1'
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
from django.core.wsgi import get_wsgi_application
if __name__=='__main__':
    make_server('127.0.0.1',8000,get_wsgi_application()).serve_forever()
