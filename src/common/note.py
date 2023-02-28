from dataclasses import dataclass

@dataclass
class Note:
    topic: str = "No topic"
    content: str = "No content"

    @staticmethod
    def loads(text):
        return Note(*text.split("</></>"))

    def dumps(self):
        return self.topic + "</></>" + self.content

    @staticmethod
    def dumps_topics(*args):
        return "<|><|>".join([arg.topic for arg in args])

    @staticmethod
    def loads_topics(text):
        return text.split("<|><|>")

    @classmethod
    def dumps_multiple(cls, *args):
        return "<|><|>".join([cls.dumps(arg) for arg in args])

    @staticmethod
    def loads_multiple(text):
        return [Note.loads(t) for t in text.split("<|><|>")]

if __name__ == "__main__":
    n = Note("topic", "content")
    print(n.dumps())
    print(Note.loads(n.dumps()))
    print(Note.loads_multiple("tp1</></>cont1<|><|>tp2</></>cont2"))
    print(Note.loads_topics("tp1<|><|>tp2<|><|>tp3<|><|>tp4"))
