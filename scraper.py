from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from info import Info

class Scraper:
  def __init__(self):
    """Initialize in-memory containers for links and bookkeeping.

    Returns:
      None
    """
    self.links_list = []
    self.links_assoc = {}
    self.info = {}
    self.append_count = 0
    self.no_append_count = 0

  def _extract_links_from_info(self, info: Info) -> List[Dict[str, str]]:
    """Base stub that child classes override to populate ``links_list``.

    Args:
      info (Info): Parsed HTML context for the current file.

    Returns:
      List[Dict[str, str]]: Defaults to an empty list.
    """
    self.links_list = []
    return self.links_list

  def _parse_html_file(self, file_path: Path) -> Optional[BeautifulSoup]:
      """Read an HTML file and parse it into BeautifulSoup.

      Args:
          file_path (Path): Path to the HTML file on disk.

      Returns:
          BeautifulSoup | None: Parsed DOM on success, otherwise ``None`` when
          the file is missing or parsing fails.
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
    """Primary scraping entry point; implemented by subclasses.

    Args:
      url (str): Resource identifier or file hint.

    Returns:
      None
    """
    pass

  def get_links_assoc_from_html(self, file_path: Path) -> List[Dict[str, str]]:
    """Parse an HTML file and return the associative course map.

    Args:
        file_path (Path): Location of the HTML snapshot.

    Returns:
        dict: ``links_assoc`` entries derived from the file.
    """
    print(f'get_links_assoc_from_html file_path.name={file_path.name}')
    assoc = {}
    if not file_path in self.info.keys():
        soup = self._parse_html_file(file_path)
        # print(f'soup={soup}')
        if soup:
            info = Info(file_path, file_path.name, soup, 0, 0)
            self.info[file_path.name] = info
            assoc = self._extract_links_assoc_from_info(info)
    # print(f'soup={soup}')
    return assoc

  def get_links_from_html(self, file_path: Path) -> List[Dict[str, str]]:
      """Parse an HTML file and return a list of course records.

      Args:
          file_path (Path): Location of the HTML snapshot.

      Returns:
          List[Dict[str, str]]: Extracted course entries.
      """
      print(f'get_links_from_html file_path.name={file_path.name}')
      links = []
      if not file_path in self.info.keys():
          soup = self._parse_html_file(file_path)
          # print(f'soup={soup}')
          if soup:
              info = Info(file_path, file_path.name, soup, 0, 0)
              self.info[file_path.name] = info
              links = self._extract_links_from_info(info)
      # print(f'soup={soup}')
      return links

  def _extract_links_from_info(self,info: Info) -> List[Dict[str, str]]:
    super()._extract_links_from_info(info)
    links_list = self.scrape(info)
    return links_list
