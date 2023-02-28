#!/usr/bin/env python

import socket
import math

from common.enums import Request, Response
from common.note import Note
from common import constants

def socket_context(func):
    def sc(conn, *args, **kwargs):
        conn.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.socket.connect((conn.host, conn.port))
        try:
            return func(conn, *args, **kwargs)
        except Exception as e:
            print("Exception in connection:", e)
        finally:
            conn.socket.close()
    return sc


class Connection:
    def __init__(self, **kwargs):
        self.host = kwargs.get("host", constants.SETTINGS["server"]["host"])
        self.port = kwargs.get("port", constants.SETTINGS["server"]["port"])
        self.token = 0
        self.socket = None

    @socket_context
    def log_in(self, uname, passwd):
        self.__send_enum(Request.LOG_IN)
        self.__send_uname(uname)
        self.__send_passwd(passwd)
        self.token = self.__recv_token()
        return self.token

    @socket_context
    def log_off(self):
        if self.token < 10_000:
            return Response.SUCCESS
        self.__send_enum(Request.LOG_OFF)
        self.__send_token()
        response = self.__recv_resp()
        if response == Response.SUCCESS:
            self.token = 0
        return response

    @socket_context
    def register(self, uname, fname, sname, passwd):
        self.__send_enum(Request.REGISTER)
        self.__send_uname(uname)
        self.__send_fname(fname)
        self.__send_sname(sname)
        self.__send_passwd(passwd)
        response = self.__recv_resp()
        return response

    @socket_context
    def create_note(self, topic, content):
        self.__send_enum(Request.CREATE_NOTE)
        self.__send_int(self.token, 2)
        self.__send_topic(topic)
        self.__send_content(content)
        print(content.encode())
        response = self.__recv_resp()
        return response

    @socket_context
    def get_notes(self):
        self.__send_enum(Request.GET_NOTES)
        self.__send_token()
        response = self.__recv_resp()
        if response == Response.SUCCESS:
            dumps = self.__recv_content()
            return Note.loads_multiple(dumps)
        return Response.FAILURE

    @socket_context
    def get_note(self, topic):
        self.__send_enum(Request.GET_NOTE)
        self.__send_token()
        self.__send_topic(topic)
        if self.__recv_resp() == Response.FAILURE:
            return Response.FAILURE
        dumps = self.__recv_content()
        print(dumps)
        return Note(topic, dumps)

    @socket_context
    def get_topics(self):
        self.__send_enum(Request.GET_TOPICS)
        self.__send_token()
        if self.__recv_resp() == Response.SUCCESS:
            return self.__recv_topics()
        return Response.FAILURE

    @socket_context
    def edit_note(self, old_topic, new_topic, content):
        self.__send_enum(Request.EDIT_NOTE)
        self.__send_token()
        self.__send_topic(old_topic)
        self.__send_topic(new_topic)
        self.__send_content(content)
        response = self.__recv_resp()
        return response

    @socket_context
    def delete_note(self, topic):
        self.__send_enum(Request.DELETE_NOTE)
        self.__send_token()
        self.__send_topic(topic)
        return self.__recv_resp()

    @socket_context
    def delete_user(self):
        self.__send_enum(Request.DELETE_USER)
        self.__send_token()
        resp = self.__recv_resp()
        if resp == Response.SUCCESS:
            self.token = 0
        return resp

    def __send_int(self, i, length):
        self.socket.send(i.to_bytes(length, "little"))

    def __send_token(self):
        self.__send_int(self.token, constants.TOKEN_BYTE_LEN)

    def __send_uname(self, s):
        self.__send_int(len(s.encode()), constants.UNAME_BYTE_LEN)
        self.__send_str(s)

    def __send_fname(self, s):
        self.__send_int(len(s.encode()), constants.FNAME_BYTE_LEN)
        self.__send_str(s)

    def __send_sname(self, s):
        self.__send_int(len(s.encode()), constants.SNAME_BYTE_LEN)
        self.__send_str(s)

    def __send_passwd(self, s):
        self.__send_int(len(s.encode()), constants.PASSWD_BYTE_LEN)
        self.__send_str(s)

    def __send_topic(self, s):
        self.__send_int(len(s.encode()), constants.TOPIC_BYTE_LEN)
        self.__send_str(s)

    def __send_content(self, s):
        self.__send_int(len(s.encode()), constants.CONTENT_BYTE_LEN)
        self.__send_str(s)

    def __send_enum(self, r):
        self.__send_int(r.value, constants.ENUM_BYTE_LEN)

    def __send_str(self, s):
        self.socket.send(str.encode(s))

    def __recv_int(self, length):
        return int.from_bytes(self.socket.recv(length), "little")

    def __recv_uname(self):
        l = self.__recv_int(constants.UNAME_BYTE_LEN)
        return self.__recv_str(l)

    def __recv_fname(self):
        l = self.__recv_int(constants.FNAME_BYTE_LEN)
        return self.__recv_str(l)

    def __recv_sname(self):
        l = self.__recv_int(constants.SNAME_BYTE_LEN)
        return self.__recv_str(l)

    def __recv_passwd(self):
        l = self.__recv_int(constants.PASSWD_BYTE_LEN)
        return self.__recv_str(l)

    def __recv_topic(self):
        l = self.__recv_int(constants.TOPIC_BYTE_LEN)
        return self.__recv_str(l)

    def __recv_topics(self):
        l = self.__recv_int(int(math.log(constants.MAXIMUM_NOTES_PER_USER, 2)))
        return [self.__recv_topic() for _ in range(l)]

    def __recv_content(self):
        l = self.__recv_int(constants.CONTENT_BYTE_LEN)
        return self.__recv_str(l)

    def __recv_token(self):
        return self.__recv_int(2)

    def __recv_str(self, length):
        return self.socket.recv(length).decode()

    def __recv_resp(self):
        return Response(self.__recv_int(1))

    def __recv_req(self):
        return Request(self.__recv_int(1))
