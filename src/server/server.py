#!/usr/bin/env python

import math
import socket
from _thread import start_new_thread
from threading import Lock
from enum import IntEnum

from database import Database
from common import constants
from common.note import Note
from common.enums import Response, Request


class Server:
    def __init__(self, server_config={}, db_config={}):
        self.tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsocket.bind(tuple((constants.SETTINGS["server"] | server_config).values()))
        self.database = Database(**(constants.SETTINGS["database"] | db_config))
        self.enable = True

    def main_loop(self):
        print(f"Listening on {self.tcpsocket.getsockname()}")
        while self.enable:
            self.tcpsocket.listen()
            (client, (ip, port) ) = self.tcpsocket.accept()
            print(f"received connection from {ip}")
            print(f"and port number {port}")
            start_new_thread(self.serve, (client, ip, port))

    def serve(self, client, ip, port):
        request = Request(int.from_bytes(client.recv(1), "little"))
        print(request)
        if   request == Request.LOG_IN   : self.log_in(client)
        elif request == Request.LOG_OFF  : self.log_off(client)
        elif request == Request.REGISTER : self.register(client)
        elif request == Request.CREATE_NOTE : self.create_note(client)
        elif request == Request.GET_NOTES: self.get_notes(client)
        elif request == Request.GET_NOTE: self.get_note(client)
        elif request == Request.GET_TOPICS: self.get_topics(client)
        elif request == Request.EDIT_NOTE: self.edit_note(client)
        elif request == Request.DELETE_NOTE: self.delete_note(client)
        elif request == Request.DELETE_USER : self.delete_user(client)
        else: self.bad_request(ip, port)

    def log_in(self, client):
        uname = self.__recv_uname(client)
        passwd = self.__recv_passwd(client)
        self.__send_token(client, self.database.log_in(uname, passwd))

    def log_off(self, client):
        token = self.__recv_token(client)
        self.__send_enum(client, self.database.log_off(token))

    def register(self, client):
        uname = self.__recv_uname(client)
        fname = self.__recv_fname(client)
        sname = self.__recv_sname(client)
        passwd = self.__recv_passwd(client)
        self.__send_enum(client, self.database.register(uname, fname, sname, passwd))

    def create_note(self, client):
        token = self.__recv_token(client)
        topic = self.__recv_topic(client)
        content = self.__recv_content(client)
        self.__send_enum(client, self.database.create_note(token, topic, content))

    def get_notes(self, client):
        token = self.__recv_token(client)
        response = self.database.get_notes(token)
        if isinstance(response, IntEnum):
            self.__send_enum(client, response)
        else:
            self.__send_enum(client, Response.SUCCESS)
            self.__send_dumps(client, response)

    def get_note(self, client):
        token = self.__recv_token(client)
        topic = self.__recv_topic(client)
        content = self.database.get_note(token, topic)
        if not content or isinstance(content, IntEnum):
            self.__send_enum(client, Response.FAILURE)
            return
        self.__send_enum(client, Response.SUCCESS)
        self.__send_content(client, content)

    def get_topics(self, client):
        token = self.__recv_token(client)
        topics = self.database.get_notes_topics(token)
        if isinstance(topics, IntEnum):
            self.__send_enum(client, Response.FAILURE)
            return
        self.__send_enum(client, Response.SUCCESS)
        self.__send_topics(client, topics)

    def edit_note(self, client):
        token = self.__recv_token(client)
        old_topic = self.__recv_topic(client)
        new_topic = self.__recv_topic(client)
        content = self.__recv_content(client)
        response = self.database.edit_note(token, old_topic, new_topic, content)
        self.__send_enum(client, response)

    def delete_note(self, client):
        token = self.__recv_token(client)
        topic = self.__recv_topic(client)
        self.__send_enum(client, self.database.delete_note(token, topic))

    def delete_user(self, client):
        token = self.__recv_token(client)
        self.__send_enum(client, self.database.delete_user(token))

    def bad_request(self, ip, port):
        print(f"WARNING: bad request from {ip}:{port}")

    def __send_int(self, client, i, length):
        client.send(i.to_bytes(length, "little"))

    def __send_token(self, client, token):
        self.__send_int(client, token, constants.TOKEN_BYTE_LEN)

    def __send_uname(self, client, s):
        self.__send_int(client, len(s.encode()), constants.UNAME_BYTE_LEN)
        self.__send_str(client, s)

    def __send_fname(self, client, s):
        self.__send_int(client, len(s.encode()), constants.FNAME_BYTE_LEN)
        self.__send_str(client, s)

    def __send_sname(self, client, s):
        self.__send_int(client, len(s.encode()), constants.SNAME_BYTE_LEN)
        self.__send_str(client, s)

    def __send_passwd(self, client, s):
        self.__send_int(client, len(s.encode()), constants.PASSWD_BYTE_LEN)
        self.__send_str(client, s)

    def __send_topic(self, client, s):
        self.__send_int(client, len(s.encode()), constants.TOPIC_BYTE_LEN)
        self.__send_str(client, s)

    def __send_topics(self, client, topics):
        self.__send_int(client, len(topics), int(math.log(constants.MAXIMUM_NOTES_PER_USER, 2)))
        for topic in topics:
            self.__send_topic(client, topic)

    def __send_content(self, client, s):
        self.__send_int(client, len(s.encode()), constants.CONTENT_BYTE_LEN)
        self.__send_str(client, s)

    def __send_enum(self, client, r):
        self.__send_int(client, r.value, constants.ENUM_BYTE_LEN)

    def __send_str(self, client, s):
        client.send(str.encode(s))

    def __send_dumps(self, client, notes):
        dumps = Note.dumps_multiple(*notes)
        self.__send_int(client, len(dumps), int(math.log(constants.MAXIMUM_NOTES_PER_USER * constants.CONTENT_BYTE_LEN)))
        self.__send_str(client, dumps)

    def __recv_int(self, client, length):
        return int.from_bytes(client.recv(length), "little")

    def __recv_uname(self, client):
        l = self.__recv_int(client, constants.UNAME_BYTE_LEN)
        return self.__recv_str(client, l)

    def __recv_fname(self, client):
        l = self.__recv_int(client, constants.FNAME_BYTE_LEN)
        return self.__recv_str(client, l)

    def __recv_sname(self, client):
        l = self.__recv_int(client, constants.SNAME_BYTE_LEN)
        return self.__recv_str(client, l)

    def __recv_passwd(self, client):
        l = self.__recv_int(client, constants.PASSWD_BYTE_LEN)
        return self.__recv_str(client, l)

    def __recv_topic(self, client):
        l = self.__recv_int(client, constants.TOPIC_BYTE_LEN)
        return self.__recv_str(client, l)

    def __recv_content(self, client):
        l = self.__recv_int(client, constants.CONTENT_BYTE_LEN)
        return self.__recv_str(client, l)

    def __recv_token(self, client):
        return self.__recv_int(client, 2)

    def __recv_str(self, client, length):
        return client.recv(length).decode("utf-8")

    def __recv_resp(self, client):
        return Response(self.__recv_int(client, 1))

    def __recv_req(self, client):
        return Request(self.__recv_int(client, 1))

    def __recv_dumps(self, client):
        l = self.__recv_int(client, int(math.log(constants.MAXIMUM_NOTES_PER_USER * constants.CONTENT_BYTE_LEN)))
        return self.__recv_str(client, l)

if __name__ == "__main__":
    Server().main_loop()
