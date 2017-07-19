# -*- coding: utf-8 -*-
import psycopg2
import contextlib

from openerp.addons.runbot import runbot
from openerp.sql_db import dsn

@contextlib.contextmanager
def local_pgadmin_cursor():
    cnx = None
    try:
        cnx = psycopg2.connect(dsn("postgres")[1])
        cnx.autocommit = True # required for admin commands
        yield cnx.cursor()
    finally:
        if cnx: cnx.close()

runbot.local_pgadmin_cursor = local_pgadmin_cursor
