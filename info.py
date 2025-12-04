from bs4 import BeautifulSoup
from pathlib import Path

class Info:
  def __init__(self, file_path: Path, name: str, soup: BeautifulSoup, append_count: int, no_append_count: int):
    """Bundle parsed HTML and bookkeeping counters.

    Args:
      file_path (Path): Source HTML path.
      name (str): Friendly identifier, typically the filename.
      soup (BeautifulSoup): Parsed DOM tree to inspect.
      append_count (int): Number of records added so far.
      no_append_count (int): Number of skipped records.

    Returns:
      None
    """
    self.file_path = file_path
    self.name = name
    self.soup = soup
    self.append_count = append_count
    self.no_append_count = no_append_count