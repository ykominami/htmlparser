from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from info import Info

class Scraper:
  def __init__(self):
    self.links_list = []
    self.links_assoc = {}
    self.info = {}
    self.append_count = 0
    self.no_append_count = 0

  def _extract_links_from_info(self, info: Info) -> List[Dict[str, str]]:
    self.links_list = []
    return self.links_list

  def _parse_html_file(self, file_path: Path) -> Optional[BeautifulSoup]:
      """
      Reads an HTML file and parses it into a BeautifulSoup object.

      This is a helper function that handles file reading and parsing.
      It returns a 'soup' object on success or None if the file is not found.

      Args:
          file_path: The path to the HTML file.

      Returns:
          A BeautifulSoup object if the file is parsed successfully, otherwise None.
      """
      try:
          with file_path.open('r', encoding='utf-8') as f:
              # Create a BeautifulSoup object using the lxml parser
              # soup = BeautifulSoup(f, 'lxml')
              soup = BeautifulSoup(f, 'html5lib')
              return soup
      except FileNotFoundError:
          print(f"Error: The file at {file_path} was not found.")
          return None
      except Exception as e:
          print(f"An error occurred: {e}")
          return None

  def scrape(self, url: str):
    pass