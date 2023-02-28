def add_source_path():
    import os
    import sys
    from pathlib import Path
    PROJECT_PATH = os.getcwd()
    SOURCE_PATH = os.path.join(Path(PROJECT_PATH, "../src").resolve())
    sys.path.append(SOURCE_PATH)
