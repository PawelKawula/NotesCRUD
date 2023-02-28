#!/usr/bin/env python

import unittest

import bcrypt

from common.utils import add_source_path
add_source_path()

from server.database import Database, Response
from common.note import Note


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.token = 0
        self.d = Database()

    def tearDown(self):
        if self.token:
            self.d.delete_note(self.token, "top1")
            self.d.delete_note(self.token, "top2")
            self.d.delete_note(self.token, "topic")
            self.d.delete_note(self.token, "new topic")
            self.d.delete_user(self.token)
            self.d.mydb.commit()
            self.d.tokens.clear()

    def __register(self):
        resp = self.d.register("test", "ftest", "stest", "secret")
        self.token = self.d.log_in("test", "secret")
        return resp

    def __log_in(self):
        self.__register()
        return self.token

    def __add_note(self):
        self.token = self.__log_in()
        return self.d.create_note(self.token, "topic", "content")

    def __get_note(self):
        self.token = self.__log_in()
        self.d.create_note(self.token, "topic", "content")
        return self.d.get_note(self.token, "topic")

    def __edit_note(self):
        self.token = self.__log_in()
        self.d.create_note(self.token, "topic", "content")
        return self.d.edit_note(self.token, "topic", "new topic", "new content")

    def test_register(self):
        self.assertEqual(self.__register(), Response.SUCCESS)

    def test_login(self):
        self.assertTrue(self.__log_in() >= 10_000)

    def test_add_note(self):
        self.assertEqual(self.__add_note(), Response.SUCCESS)

    def test_get_note(self):
        self.assertEqual(self.__get_note(), "content")

    def test_edit_note(self):
        self.assertEqual(self.__edit_note(), Response.SUCCESS)

    def test_get_and_delete_notes(self):
        self.token = self.__log_in()
        self.d.create_note(self.token, "top1", "cont1")
        self.d.create_note(self.token, "top2", "cont2")
        notes = self.d.get_notes(self.token)
        self.assertEqual(notes[0].topic, "top1")
        self.assertEqual(notes[1].topic, "top2")
        self.d.delete_note(self.token, "top1")
        self.d.delete_note(self.token, "top2")
        self.assertEqual(self.d.get_notes(self.token), [])


if __name__ == "__main__":
    unittest.main()
