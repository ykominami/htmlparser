from bs4 import BeautifulSoup
from pathlib import Path

class Info:
  def __init__(self, mode: str, file_path: Path, name: str, soup: BeautifulSoup, append_count: int, no_append_count: int):
    self.mode = mode
    self.file_path = file_path
    self.name = name
    self.soup = soup
    self.append_count = append_count
    self.no_append_count = no_append_count