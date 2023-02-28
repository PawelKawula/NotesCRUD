class CrudMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Crud(metaclass=CrudMeta):
    def select_login(self, uname, passwd):
        pass

    def user_logoff(self, token):
        pass

    def create_note(self, token, topic, content):
        pass

    def get_notes(self, token):
        pass

    def delete_note(self, token, note_id):
        pass

    def edit_note(self, token, note_id, content, topic=None):
        pass

