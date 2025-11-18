from scraper import Scraper
from info import Info
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from pathlib import Path

class KUScraper(Scraper):
  def __init__(self):
    super().__init__()

  def scrape(self, info: Info) -> List[Dict[str, str]]:
    print('kuscraper scrape')
    soup = info.soup
    append_count = 0
    no_append_count = 0
    """aの処理"""
    for a_tag in soup.find_all('a'):
        # classが"a-link-normal"でない場合はcontinue
        if a_tag.get('class') != ['a-link-normal']:
            print(f'a_tag.get("class")={a_tag.get("class")}')
            continue

    return self.links_list

  def _extract_links_from_info(self,info: Info) -> List[Dict[str, str]]:
    super()._extract_links_from_info(info)
    links_list = self.scrape(info)
    return links_list


  def get_links_from_html(self, file_path: Path) -> List[Dict[str, str]]:
      """
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
