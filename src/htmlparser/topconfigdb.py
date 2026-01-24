from pathlib import Path
from typing import Any, List

from yklibpy.common.env import Env


class TopConfigDb:
  def __init__(self, parent_path: Path, assoc: dict[str, Any]):
    self.sequence = 0
    self.assoc = assoc
    self.db_kind: str | None = assoc.get("db_kind", None)
    self.patterns: List[str] = assoc.get("patterns", ["Amazon-KU-1-file"])
    self.db_file: str | None = assoc.get("db_file", None)
    self.db_file_path: Path | None = None
    self.main_config: dict[str, dict[str, Any]] = {}
    self.env = None

    if self.db_file is not None:
      self.parent_path = parent_path
      self.db_file_path = self.parent_path / self.db_file

    self.config_file =  self.assoc.get("config_file", None)
    print(f'self.config_file={self.config_file}')
    if self.config_file is not None:
      self.config_file_path = self.parent_path / self.config_file
      print(f'self.config_file_path={self.config_file_path}')
      self.env = Env(self.config_file_path)
      # raise Exception(f"env:__init__ self.config_file_path={self.config_file_path}")

  def get_env(self) -> Env:
    return self.env

  def get_patterns(self) -> List[str]:
    return self.patterns

  def get_db_file_path(self) -> Path | None:
    return self.db_file_path

  def get_db_file_name(self) -> str | None:
    return self.db_file

  def get_db_kind(self) -> str | None:
    return self.db_kind
