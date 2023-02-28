#!/usr/bin/env python

from enum import IntEnum

import mysql.connector
from mysql.connector.errors import IntegrityError
import bcrypt

from common.enums import Response
from common.note import Note
from common import constants

def token_generator():
    i = 10_000
    while True:
        yield i
        i += 1

class DatabaseMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=DatabaseMeta):
    def __init__(self, **kwargs):
        self.mydb = mysql.connector.connect(**(constants.SETTINGS["database"] | kwargs))
        self.gen_token = token_generator()
        self.tokens = {}

    def log_in(self, uname, passwd):
        sql = "Select passwd FROM users WHERE uname=%s"
        cursor = self.mydb.cursor()
        cursor.execute(sql, (uname,))
        fetch = cursor.fetchone()
        if not fetch or len(fetch) == 0:
            return Response.WRONG_CREDENTIALS
        enc_hashed = bytes(fetch[0], "utf-8")
        if not bcrypt.checkpw(passwd.encode("utf-8"), enc_hashed):
            return Response.WRONG_CREDENTIALS
        if uname in self.tokens:
            return Response.ALREADY_LOGGED_IN
        token = next(self.gen_token)
        self.tokens[uname] = token
        return token

    def log_off(self, token):
        for k, v in self.tokens.items():
            if v == token:
                if k in self.tokens:
                    del self.tokens[k]
                return Response.SUCCESS
        return Response.FAILURE

    def register(self, uname, fname, sname, passwd):
        sql = "INSERT INTO users(uname, passwd, fname, sname) values(%s, %s, %s, %s)"
        cursor = self.mydb.cursor()
        try:
            passwd = bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(sql, (uname, passwd, fname, sname))
            self.mydb.commit()
        except IntegrityError:
            return Response.USER_ALREADY_REGISTERED
        return Response.SUCCESS if cursor.rowcount else Response.FAILURE

    def __get_user_id(self, cursor, uname):
        sql = "SELECT userId FROM users WHERE uname = %s"
        cursor.execute(sql, (uname,))
        fetch = cursor.fetchone()
        return fetch[0] if fetch else None

    def create_note(self, token, topic, content):
        for k, v in self.tokens.items():
            if v == token:
                cursor = self.mydb.cursor()
                sql = "INSERT INTO notes(userId, topic, content) VALUES(%s, %s, %s)"
                user_id = self.__get_user_id(cursor, k)
                if not user_id:
                    return Response.FAILURE
                try:
                    cursor.execute(sql, (user_id, topic, content))
                    self.mydb.commit()
                except IntegrityError:
                    return Response.TOPIC_ALREADY_EXISTS
                return Response.SUCCESS
        return Response.FAILURE


    def get_notes(self, token):
        for k, v in self.tokens.items():
            if v == token:
                sql = "SELECT topic, content FROM notes inner join users on users.userId=notes.userId WHERE users.uname=%s"
                cursor = self.mydb.cursor()
                cursor.execute(sql, (k,))
                fetch = cursor.fetchall()
                return [Note(*args) for args in fetch]
        return Response.FAILURE

    def get_notes_topics(self, token):
        for k, v in self.tokens.items():
            if v == token:
                cursor = self.mydb.cursor()
                user_id = self.__get_user_id(cursor, k)
                sql = "SELECT topic FROM notes WHERE userId=%s"
                cursor.execute(sql, (user_id,))
                return [ topic for (topic,) in cursor.fetchall() ]
        return Response.FAILURE

    def get_note(self, token, topic):
        for k, v in self.tokens.items():
            if v == token:
                cursor = self.mydb.cursor()
                user_id = self.__get_user_id(cursor, k)
                sql = "SELECT content FROM notes WHERE userId=%s AND topic=%s"
                cursor.execute(sql, (user_id, topic))
                fetch = cursor.fetchone()
                return fetch[0] if fetch is not None else None
        return Response.FAILURE

    def edit_note(self, token, old_topic, new_topic, content):
        for k, v in self.tokens.items():
            if v == token:
                cursor = self.mydb.cursor()
                user_id = self.__get_user_id(cursor, k)
                sql = "UPDATE notes SET topic=%s,content=%s WHERE userId=%s AND topic=%s"
                val = (new_topic, content, user_id, old_topic)
                cursor.execute(sql, val)
                self.mydb.commit()
                if cursor.rowcount:
                    return Response.SUCCESS
                else:
                    return Response.NO_NOTE_WITH_THAT_TOPIC
        return Response.FAILURE

    def delete_note(self, token, topic):
        for k, v in self.tokens.items():
            if v == token:
                cursor = self.mydb.cursor()
                user_id = self.__get_user_id(cursor, k)
                sql = "DELETE FROM notes where userid=%s AND topic=%s"
                cursor.execute(sql, (user_id, topic))
                self.mydb.commit()
                return Response.SUCCESS if cursor.rowcount else Response.NO_NOTE_WITH_THAT_TOPIC
        return Response.FAILURE

    def delete_user(self, token):
        for k, v in self.tokens.items():
            if v == token:
                cursor = self.mydb.cursor()
                sql = "DELETE FROM users where uname=%s"
                cursor.execute(sql, (k,))
                self.mydb.commit()
                if cursor.rowcount:
                    del self.tokens[k]
                    return Response.SUCCESS
                return Response.FAILURE
        return Response.FAILURE
