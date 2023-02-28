#!/usr/bin/env python

import unittest

import bcrypt

from common.utils import add_source_path
add_source_path()

from server.database import Response
from server.server import Server
from client.connection import Connection
from common.note import Note


class ConnectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
