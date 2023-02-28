import os
from pathlib import Path

UNAME_BYTE_LEN = 2
FNAME_BYTE_LEN = 2
SNAME_BYTE_LEN = 2
PASSWD_BYTE_LEN = 4
TOKEN_BYTE_LEN = 2
TOPIC_BYTE_LEN = 2
CONTENT_BYTE_LEN = 4
ENUM_BYTE_LEN = 1
MAXIMUM_NOTES_PER_USER = 1024
# SALT = b"$2b$12$./Tp7YPFUQ1qowUOZgcu8."
SRC_PATH = Path(os.path.realpath(__file__)).parent.parent
PROJECT_ROOT = SRC_PATH.parent
TEST_PATH = PROJECT_ROOT/"tests"

assert SRC_PATH.exists(), "Source Path does not exist!"
assert PROJECT_ROOT.exists(), "Project root Path does not exist!"
assert TEST_PATH.exists(), "Tests Path does not exist!"

def get_settings(filepath: Path=PROJECT_ROOT/"settings.toml"):
    assert filepath.exists(), "Settings file does not exist!"
    try:
        import tomllib as tomli
    except:
        import tomli
    conf = {}
    with open(filepath, "rb") as f:
        conf = tomli.load(f)
    env = { k: os.getenv(k) for k in ["DATABASE_HOST", "DATABASE_USER", "DATABASE_PORT" "DATABASE_PASSWORD", "DATABASE_DB", "SERVER_HOST", "SERVER_PORT"] if os.getenv(k) }
    for k, v in env.items():
        k1, k2 = map(lambda x: x.lower(), k.split("_"))
        conf[k1][k2] = v
    return conf

SETTINGS = get_settings()
