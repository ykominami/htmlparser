import sys
from pathlib import Path
from typing import Any, NamedTuple

from yklibpy.common.util_yaml import UtilYaml
from yklibpy.db import get_or_create_db
from yklibpy.htmlparser import App, Preparex

from .topconfigdb import TopConfigDb


class ConfigFileInfo(NamedTuple):
    parent_path: Path
    assoc: dict[str, dict[str, Any]]

class Top:
    def __init__(self, parent_path: Path, assoc: dict[str, dict[str, Any]]):
        self.top_config = TopConfigDb(parent_path, assoc)
        self.setup()

    def setup(self) -> None:
        self.patterns = self.top_config.get_patterns()

        self.db_file_path = self.top_config.get_db_file_path()
        self.db_kind = self.top_config.get_db_kind()
        self.db = get_or_create_db(self.db_kind, self.db_file_path)

    def db_loadx(self) -> None:
        tag  = 'tag:yaml.org,2002:python/object:yklibpy.htmlparser.amazonsavedcartscraper.WorkInfo'
        tags = [tag]
        self.db.load(tags=tags)

    def db_load(self, tags:list[Any]=[]) -> None:
        self.db.load(tags=tags)

    def save(self) -> None :
        self.db.save()

    def db_count(self) -> None :
        print(f'count={self.db.count()}')

    def db_print_list_text(self, key: str) -> None:
        for text in self.db.list_text(key):
            print(text)

    @classmethod
    def prepare(cls, parent_path: Path, assoc: dict[str, dict[str, Any]], category: str) -> None:
        print("Top prepare")
        top_path = parent_path.parent
        print(f'top_path={top_path}')
        Preparex(str(top_path), category, str(parent_path), assoc)

def get_yaml_path() -> Path:
    cmd_file = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd_file is None:
        raise Exception("cmd_file is not set")

    cmd_file_path = Path(cmd_file)
    return cmd_file_path

def load_config_file() -> ConfigFileInfo:
    cmd_file_path = get_yaml_path()
    print(f'cmd_file_path={cmd_file_path}')
    assoc = UtilYaml.load_yaml(cmd_file_path)
    parent_path = cmd_file_path.parent
    return ConfigFileInfo(parent_path, assoc)

def amain() -> None:
    [parent_path, assoc] = load_config_file()
    print("amain")
    top = Top(parent_path, assoc)
    top.db_loadx()
    db_assoc = top.db.get_data()

    app = App()
    app.links_assoc.update(db_assoc)
    print(f'len(app.links_assoc)={ len(app.links_assoc) }')
    patterns = top.top_config.get_patterns()
    for pattern in patterns:
        env = top.top_config.get_env()
        ret = env.set_pattern(pattern)
        if ret is None:
            mes = f'invalid result ret={ret} pattern={pattern}'
            raise ValueError(mes)
        # print(f'env={env}')
        app.run(env)

    # app.links_assoc.update(db_assoc)
    top.db.set_data(app.links_assoc)
    top.db.save()

    top.db_count()

def clearmain() -> int:
    [parent_path, assoc] = load_config_file()
    print("clearmain")
    top = Top(parent_path, assoc)
    top.db.clear()
    top.db.save()

    return 0

def count() -> int:
    [parent_path, assoc] = load_config_file()
    print("count")
    top = Top(parent_path, assoc)
    top.db_loadx()
    db_assoc = top.db.get_data()

    app = App()
    app.links_assoc.update(db_assoc)
    print(f'len(app.links_assoc)={ len(app.links_assoc) }')

    top.db_count()

    return 0

def print_list_text() -> None:
    [parent_path, assoc] = load_config_file()
    print("print_list_text")
    top = Top(parent_path, assoc)
    top.db_loadx()
    top.db_print_list_text("title")

def prepare() -> None:
    [parent_path, assoc] = load_config_file()
    print("prepare")
    category = "htmlparser"
    Top.prepare(parent_path, assoc, category)
