from enum import Enum, IntEnum
import os, subprocess, tempfile

from client.connection import Connection
from common.enums import Response

class View:
    class Controls(Enum):
        LOG_IN = 'l'
        LOG_OFF = 'o'
        REGISTER = 'r'
        PREVIEW_NOTES = 'p'
        DELETE_NOTE = 'd'
        DELETE_USER = 'u'
        CREATE_NOTE = 'c'
        EDIT_NOTE = 'e'
        QUIT = 'q'
        YES = 'y'
        NO = 'n'

    LOGGED_OUT_INPUT_UNAME = "Wpisz swój login: "
    LOGGED_OUT_INPUT_FNAME = "Wpisz swoje imie: "
    LOGGED_OUT_INPUT_SNAME = "Wpisz swoje nazwisko: "
    LOGGED_OUT_INPUT_PASSWD = "Wpisz swoje hasło: "
    LOGGED_OUT_REPEAT_PASSWD = "Powtórz swoje hasło: "
    LOGGED_IN_MENU = f"Aby się wylogować, wpisz {Controls.LOG_IN.value}\n"\
                f"Aby przejrzeć swoje notatki, wpisz {Controls.PREVIEW_NOTES.value}\n"\
                f"Aby usunąć notatkę, wpisz {Controls.DELETE_NOTE.value}\n"\
                f"Aby utworzyć notatkę, wpisz {Controls.CREATE_NOTE.value}\n"\
                f"Aby edytować notatkę, wpisz {Controls.EDIT_NOTE.value}\n"\
                f"Aby usunąć swoje konto, wpisz {Controls.DELETE_USER.value}\n"\
                f"Aby wyjść, wpisz {Controls.QUIT.value}: "
    LOGGED_OFF_MENU = f"Aby się zarejestrować, wpisz {Controls.REGISTER.value}\n"\
                        f"Aby się zalogować, wpisz {Controls.LOG_IN.value}\n"\
                        f"Aby wyjść, wpisz {Controls.QUIT.value}: "
    INPUT_TOPIC = f"Wprowadź tytuł swojej notatki: "
    INPUT_NEW_TOPIC = f"Wprowadź nowy tytuł: "
    CHOOSE_NOTE_EDIT = f"Wybierz notatke po numerze ({Controls.QUIT.value} aby wyjść): "
    CHOOSE_NOTE_DELETE = f"Wybierz notatke która chcesz usunąć: "
    CHOOSE_NOTE_PREVIEW = f"Wybierz którą notatkę chcesz przejrzeć ({Controls.QUIT.value} aby wyjść): "
    NOTE_DELETE_AYS = "Jesteś pewny że chcesz usunąć notatkę o tytule %s?: "
    USER_DELETE_AYS = "Jesteś pewny że chcesz usunąć swoje konto?: "

    def __init__(self):
        self.connection, self.uname = Connection(), None

    def menu(self):
        while True:
            if self.is_logged():
                inp = input(self.LOGGED_IN_MENU)
                if inp == self.Controls.LOG_IN.value:
                    self.log_off()
                elif inp == self.Controls.PREVIEW_NOTES.value:
                    self.preview_notes()
                elif inp == self.Controls.DELETE_NOTE.value:
                    self.delete_note()
                elif inp == self.Controls.CREATE_NOTE.value:
                    self.create_note()
                elif inp == self.Controls.EDIT_NOTE.value:
                    self.edit_note()
                elif inp == self.Controls.DELETE_USER.value:
                    self.delete_user()
                elif inp == self.Controls.QUIT.value:
                    self.log_off()
                    print("Pa pa")
                    return
                else:
                    print("Nieprawidlowa opcja!")
            else:
                if not self.register_or_login():
                    print("Pa pa")
                    return

    def set_connection(self, connection):
        self.connection = connection

    def is_logged(self):
        return int(self.connection.token) >= 10_000

    def log_off(self):
        self.connection.log_off()

    def connection_set_assertion(self):
        assert self.connection is not None, "Server must be set before this operation!"

    def log_in(self):
        uname = input(self.LOGGED_OUT_INPUT_UNAME)
        passwd = input(self.LOGGED_OUT_INPUT_PASSWD)
        self.connection_set_assertion()
        token = self.connection.log_in(uname, passwd)
        print()
        if  token >= 10_000:
            print("Zalogowano")
        else:
            print("Logowanie nieudane!")

    def register(self):
        uname = input(self.LOGGED_OUT_INPUT_UNAME)
        fname = input(self.LOGGED_OUT_INPUT_FNAME)
        sname = input(self.LOGGED_OUT_INPUT_SNAME)
        passwd = input(self.LOGGED_OUT_INPUT_PASSWD)
        passwd2 = input(self.LOGGED_OUT_REPEAT_PASSWD)
        if passwd != passwd2:
            print("Hasła nie zgadzają się!")
            return
        self.connection_set_assertion()
        return self.connection.register(uname, fname, sname, passwd)

    def register_or_login(self):
        self.connection_set_assertion()
        while True:
            inp = input(self.LOGGED_OFF_MENU)
            if inp == self.Controls.REGISTER.value:
                self.register()
            elif inp == self.Controls.LOG_IN.value:
                self.log_in()
                return True
            elif inp == self.Controls.QUIT.value:
                return False
            else:
                print("Nieprawidlowa opcja")

    def preview_topics(self):
        self.connection_set_assertion()
        topics = self.connection.get_topics()
        en_topics = list(enumerate(topics))
        for i, topic in en_topics:
            print(f"{i}. {topic}")
        return en_topics

    def preview_notes(self):
        en_topics = self.preview_topics()
        inp = input(self.CHOOSE_NOTE_PREVIEW)
        if inp == self.Controls.QUIT:
            return
        if len(en_topics) == 0:
            print("Brak notatek!")
            return
        if not str.isnumeric(inp) or 0 > int(inp) or int(inp) >= len(en_topics):
            print("Nieprawidłowy zakres")
            return
        inp = int(inp)
        note = self.connection.get_note(en_topics[inp][1])
        path = self.__tempfile_vim(note.content)
        os.unlink(path)

    def delete_note(self):
        en_topics = self.preview_topics()
        i = input(self.CHOOSE_NOTE_DELETE)
        if len(en_topics) == 0:
            print("Brak notatek!")
            return
        if not str.isnumeric(i) or 0 > int(i) or int(i) >= len(en_topics):
            print("Nieprawidłowy zakres")
            return
        i = int(i)
        ys = input(self.NOTE_DELETE_AYS % en_topics[i][1])
        if ys == self.Controls.YES.value:
            if self.connection.delete_note(en_topics[i][1]) == Response.SUCCESS:
                print("Usunięto notatkę")
            else:
                print("Niepowodzenie")
        elif ys == self.Controls.NO.value:
            print("Anulowano usuwanie")
        else:
            print("Nieprawidlowa opcja!")

    def delete_user(self):
        ys = input(self.USER_DELETE_AYS)
        if ys == self.Controls.YES.value:
            self.connection.delete_user()
            self.connection.log_off()
        elif ys == self.Controls.NO.value:
            print("Anulowano usuwanie")
        else:
            print("Nieprawidlowa opcja")

    def __tempfile_vim(self, content):
        (fd, path) = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(content)
        fp.close()
        editor = os.getenv('EDITOR', 'vi')
        subprocess.call('%s %s' % (editor, path), shell=True)
        return path

    def create_note(self):
        topic = input(self.INPUT_TOPIC)
        path = self.__tempfile_vim("Nowa notatka")
        with open(path, 'r') as f:
            content = f.read()
            if len(content) and content != "Nowa notatka":
                response = self.connection.create_note(topic, content)
                if response == Response.SUCCESS:
                    print("Dodano notatke")
                else:
                    print("Niepowodzenie")
            else:
                print("Anulowano")
        os.unlink(path)

    def edit_note(self):
        topic = input(self.INPUT_TOPIC)
        topics = self.connection.get_topics()
        if isinstance(topics, Response):
            print("Błąd! połączenia: {topics}")
            return
        if topic not in topics:
            print("Błąd! Nie ma takiej notatki do edycji!")
            return
        new_topic = input(self.INPUT_NEW_TOPIC)
        if topic and topic != "\n":
            note = self.connection.get_note(topic)
            if isinstance(note, IntEnum):
                print("Odpowiedź:", note)
                return
            path = self.__tempfile_vim(note.content)
            with open(path, 'r') as f:
                self.connection.edit_note(topic, new_topic, f.read())
            os.unlink(path)

if __name__ == "__main__":
    View().menu()
