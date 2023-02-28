from enum import IntEnum

class Response(IntEnum):
    SUCCESS = 0
    ALREADY_LOGGED_IN = 1
    WRONG_CREDENTIALS = 2
    USER_ALREADY_REGISTERED = 3
    FAILURE = 4
    TOPIC_ALREADY_EXISTS = 5
    NO_NOTE_WITH_THAT_TOPIC = 6

class Request(IntEnum):
    LOG_IN     = 0
    LOG_OFF    = 1
    REGISTER   = 2
    CREATE_NOTE   = 3
    GET_NOTES  = 4
    GET_NOTE   = 5
    EDIT_NOTE  = 6
    DELETE_NOTE = 7
    DELETE_USER = 8
    GET_TOPICS = 9

