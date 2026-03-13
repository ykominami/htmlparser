import argparse
from pathlib import Path
from typing import Any, Callable, NamedTuple, cast

from yklibpy.cli import Cli
from yklibpy.common.util_yaml import UtilYaml
from yklibpy.db import DbYaml, get_or_create_db

from htmlparser.subapp import Subapp
from htmlparser.topconfigdb import TopConfigDb

type CommandFunc = Callable[[argparse.Namespace], int | None]


class ConfigFileInfo(NamedTuple):
    parent_path: Path
    assoc: dict[str, dict[str, Any]]


class RuntimeInfo(NamedTuple):
    top_config: TopConfigDb
    db: DbYaml


class Clix:
    def __init__(
        self,
        description: str,
        command_dict: dict[str, CommandFunc] | None = None,
    ) -> None:
        self.cli = Cli(description)
        command_dict = command_dict or self.build_command_dict()
        subparsers = self.cli.get_subparsers("command")

        p_run = subparsers.add_parser("run", help="parse HTML files and update DB")
        p_run.set_defaults(func=command_dict["run"])
        p_run.add_argument("config_file", help="YAML config file path")

        p_clear = subparsers.add_parser("clear", help="clear DB data")
        p_clear.set_defaults(func=command_dict["clear"])
        p_clear.add_argument("config_file", help="YAML config file path")

        p_count = subparsers.add_parser("count", help="print DB entry count")
        p_count.set_defaults(func=command_dict["count"])
        p_count.add_argument("config_file", help="YAML config file path")

        p_print = subparsers.add_parser(
            "print-list-text", help="print DB values for a key"
        )
        p_print.set_defaults(func=command_dict["print-list-text"])
        p_print.add_argument("config_file", help="YAML config file path")
        p_print.add_argument("--key", default="title", help="DB text field name")

    def parse_args(self) -> argparse.Namespace:
        return self.cli.parse_args()

    def build_command_dict(self) -> dict[str, CommandFunc]:
        return {
            "run": self.run_command,
            "clear": self.clear_command,
            "count": self.count_command,
            "print-list-text": self.print_list_text_command,
        }

    def resolve_config_path(self, args: argparse.Namespace) -> Path:
        config_file = getattr(args, "config_file", None)
        if not isinstance(config_file, str):
            raise ValueError("config_file is not set")
        if config_file == "":
            raise ValueError("config_file is empty")

        return Path(config_file)

    def load_config_file_from_args(self, args: argparse.Namespace) -> ConfigFileInfo:
        config_path = self.resolve_config_path(args)
        assoc_any = UtilYaml.load_yaml(config_path)
        if not isinstance(assoc_any, dict):
            raise ValueError("config file must contain a mapping")

        assoc = cast(dict[str, dict[str, Any]], assoc_any)
        return ConfigFileInfo(config_path.parent, assoc)

    def build_runtime_from_args(self, args: argparse.Namespace) -> RuntimeInfo:
        parent_path, assoc = self.load_config_file_from_args(args)
        top_config = TopConfigDb(parent_path, assoc)

        db_file_path = top_config.get_db_file_path()
        if db_file_path is None:
            raise ValueError("db_file is not set")

        db_kind = top_config.get_db_kind()
        if db_kind is None:
            raise ValueError("db_kind is not set")

        db = get_or_create_db(db_kind, str(db_file_path))
        if db is None:
            raise ValueError(f"unsupported db_kind={db_kind}")

        return RuntimeInfo(top_config, db)

    def db_loadx(self, db: DbYaml) -> None:
        tag = "tag:yaml.org,2002:python/object:htmlparser.amazonsavedcartscraper.WorkInfo"
        tag2 = (
            "tag:yaml.org,2002:python/object:htmlparser.fanzadoujinbasketscraper.WorkInfo"
        )
        db.load(tags=[tag, tag2])

    def db_count(self, db: DbYaml) -> None:
        print(f"count={db.count()}")

    def db_print_list_text(self, db: DbYaml, key: str) -> None:
        for text in db.list_text(key):
            print(text)

    def run_command(self, args: argparse.Namespace) -> int:
        runtime = self.build_runtime_from_args(args)
        self.db_loadx(runtime.db)
        db_assoc = runtime.db.get_data()

        app = Subapp()
        app.links_assoc.update(db_assoc)

        for pattern in runtime.top_config.get_patterns():
            env = runtime.top_config.get_env()
            if env is None:
                continue

            ret = env.set_pattern(pattern)
            if ret is None:
                raise ValueError(f"invalid result ret={ret} pattern={pattern}")
            app.run(env)

        runtime.db.set_data(app.links_assoc)
        runtime.db.save()
        self.db_count(runtime.db)
        return 0

    def clear_command(self, args: argparse.Namespace) -> int:
        runtime = self.build_runtime_from_args(args)
        runtime.db.clear()
        runtime.db.save()
        return 0

    def count_command(self, args: argparse.Namespace) -> int:
        runtime = self.build_runtime_from_args(args)
        self.db_loadx(runtime.db)
        self.db_count(runtime.db)
        return 0

    def print_list_text_command(self, args: argparse.Namespace) -> int:
        runtime = self.build_runtime_from_args(args)
        self.db_loadx(runtime.db)
        key = getattr(args, "key", "title")
        self.db_print_list_text(runtime.db, key if isinstance(key, str) else "title")
        return 0


def main() -> int:
    clix = Clix("HTML parser utility")
    args = clix.parse_args()
    return int(args.func(args) or 0)
